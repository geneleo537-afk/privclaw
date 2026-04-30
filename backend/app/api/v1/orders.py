"""
订单端点：创建、查询、取消、状态轮询、余额支付。

POST /orders                        — 创建订单
GET  /orders/{order_id}             — 订单详情
POST /orders/{order_id}/cancel      — 买家取消订单
GET  /orders/{order_id}/status      — 轮询支付状态（前端用）
POST /orders/{order_id}/pay/balance — 余额支付（即时完成）

支付宝支付入口在 payments.py 中实现（POST /orders/{order_id}/pay/alipay）。
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import case as sa_case, func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.order import Order, UserPurchase
from app.models.plugin import Plugin
from app.models.user import User
from app.models.wallet import Transaction
from app.schemas.common import Response
from app.schemas.order import CreateOrderRequest, OrderResponse

router = APIRouter()

# 平台抽成费率（30%）
PLATFORM_FEE_RATE = Decimal("0.30")
# 订单过期时间（分钟）
ORDER_EXPIRE_MINUTES = 30


def _to_order_response(order: Order) -> OrderResponse:
    """将 Order ORM 对象转换为 OrderResponse Schema。"""
    return OrderResponse(
        id=order.id,
        order_no=order.order_no,
        plugin_snapshot=order.plugin_snapshot,
        paid_amount=order.paid_amount,
        platform_fee=order.platform_fee,
        developer_revenue=order.developer_revenue,
        pay_channel=order.payment_channel or None,
        status=order.status,
        paid_at=order.paid_at,
        expires_at=order.expires_at,
        created_at=order.created_at,
    )


def _generate_order_no() -> str:
    """
    生成平台订单号。

    格式：LC + 年月日(8位) + UUID 前 8 位十六进制
    示例：LC20260311a1b2c3d4
    """
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:8]
    return f"LC{date_str}{unique_part}"


async def _calc_user_balance(user_id: uuid.UUID, db: AsyncSession) -> Decimal:
    """
    计算用户账户余额：累计入账 - 累计出账（仅 status='completed' 的流水）。

    此函数为纯读操作，可在任意需要余额的路由中复用。
    """
    result = await db.execute(
        select(
            sa_func.coalesce(
                sa_func.sum(
                    sa_case(
                        (Transaction.direction == "in", Transaction.amount),
                        else_=-Transaction.amount,
                    )
                ),
                Decimal("0.00"),
            )
        ).where(
            Transaction.user_id == user_id,
            Transaction.status == "completed",
        )
    )
    return result.scalar_one() or Decimal("0.00")


def _new_tx_no() -> str:
    """生成唯一交易流水号：TX + 时间戳(14位) + UUID 前 8 位。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TX{ts}{uuid.uuid4().hex[:8]}"


@router.post(
    "/orders",
    response_model=Response[OrderResponse],
    status_code=201,
    summary="创建订单",
)
async def create_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[OrderResponse]:
    """
    为指定插件创建购买订单。

    前置校验：
    1. 插件必须存在且已发布（status='published'）
    2. 用户不能重复购买同一插件（user_purchases 表唯一约束保护）
    3. 免费插件直接标记为 paid 并写入 user_purchases，跳过支付流程

    付费订单创建后，向 Celery 投递 30 分钟超时关闭任务。
    """
    # 验证插件存在且已发布
    plugin_result = await db.execute(
        select(Plugin).where(
            Plugin.id == req.plugin_id,
            Plugin.status == "published",
            Plugin.deleted_at.is_(None),
        )
    )
    plugin: Optional[Plugin] = plugin_result.scalar_one_or_none()
    if plugin is None:
        raise NotFoundError("插件不存在或尚未发布")

    # 检查是否已购买（幂等保护）
    existing_purchase = await db.execute(
        select(UserPurchase).where(
            UserPurchase.user_id == current_user.id,
            UserPurchase.plugin_id == req.plugin_id,
        )
    )
    if existing_purchase.scalar_one_or_none():
        raise ConflictError("您已购买过此插件，无需重复购买")

    # 计算分账金额
    paid_amount = plugin.price
    platform_fee = (paid_amount * PLATFORM_FEE_RATE).quantize(Decimal("0.01"))
    developer_revenue = (paid_amount - platform_fee).quantize(Decimal("0.01"))

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ORDER_EXPIRE_MINUTES)

    # 构建插件快照（固化当前时刻的插件信息，防止插件修改后历史订单数据失真）
    plugin_snapshot = {
        "plugin_id": str(plugin.id),
        "name": plugin.name,
        "version": plugin.current_version,
        "price": str(plugin.price),
        "currency": plugin.currency,
        "icon_url": plugin.icon_url,
        "summary": plugin.summary,
    }

    order = Order(
        id=uuid.uuid4(),
        order_no=_generate_order_no(),
        buyer_id=current_user.id,
        plugin_id=plugin.id,
        plugin_version_id=plugin.current_version_id,
        developer_id=plugin.developer_id,
        original_price=plugin.price,
        paid_amount=paid_amount,
        platform_fee=platform_fee,
        developer_revenue=developer_revenue,
        fee_rate=PLATFORM_FEE_RATE,
        status="pending",
        expires_at=expires_at,
        plugin_snapshot=plugin_snapshot,
    )
    db.add(order)
    await db.flush()

    if plugin.is_free:
        # 免费插件：直接完成，无需支付
        order.status = "paid"
        order.paid_at = now
        db.add(order)

        purchase = UserPurchase(
            id=uuid.uuid4(),
            user_id=current_user.id,
            plugin_id=plugin.id,
            order_id=order.id,
        )
        db.add(purchase)
    else:
        # 付费插件：投递 Celery 超时任务，30 分钟后自动关闭
        celery_app.send_task(
            "app.tasks.order_timeout.close_expired_order",
            args=[str(order.id)],
            countdown=ORDER_EXPIRE_MINUTES * 60,
        )

    return Response.ok(data=_to_order_response(order), message="订单创建成功")


@router.get(
    "/orders/{order_id}",
    response_model=Response[OrderResponse],
    summary="订单详情",
)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[OrderResponse]:
    """
    查询指定订单详情。买家只能查看自己的订单，管理员可查看全部订单。
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if current_user.role != "admin" and order.buyer_id != current_user.id:
        raise ForbiddenError("无权限查看此订单")

    return Response.ok(data=_to_order_response(order))


@router.post(
    "/orders/{order_id}/cancel",
    response_model=Response[None],
    summary="取消订单",
)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[None]:
    """
    买家主动取消待支付订单。

    - 仅允许取消 status='pending' 的订单
    - 已支付、已关闭、已退款的订单不可取消
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if order.buyer_id != current_user.id:
        raise ForbiddenError("无权限操作此订单")

    if order.status != "pending":
        raise BadRequestError(f"当前订单状态为 '{order.status}'，无法取消")

    order.status = "cancelled"
    order.cancelled_at = datetime.now(timezone.utc)
    db.add(order)

    return Response.ok(message="订单已取消")


@router.get(
    "/orders/{order_id}/status",
    response_model=Response[dict],
    summary="轮询订单支付状态",
)
async def order_status(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    前端支付等待页面轮询端点，返回轻量化状态信息。

    建议前端每 2-3 秒调用一次，直到 status 变为 'paid' 或 'closed'/'cancelled'。
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if order.buyer_id != current_user.id:
        raise ForbiddenError("无权限查询此订单")

    return Response.ok(
        data={
            "order_id": str(order.id),
            "order_no": order.order_no,
            "status": order.status,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "expires_at": order.expires_at.isoformat() if order.expires_at else None,
        }
    )


@router.post(
    "/orders/{order_id}/pay/balance",
    response_model=Response[OrderResponse],
    summary="余额支付",
)
async def pay_with_balance(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[OrderResponse]:
    """
    使用账户余额即时支付订单，无需跳转第三方支付页面。

    执行步骤：
    1. 验证订单状态为 pending 且未过期
    2. 计算买家当前余额（Transaction 表累计差值）
    3. 验证余额充足
    4. 写入买家扣款流水（direction='out', type='payment'）
    5. 更新订单状态为 paid
    6. 写入 user_purchases 记录
    7. 写入开发者入账流水（direction='in', type='settlement'）
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if order.buyer_id != current_user.id:
        raise ForbiddenError("无权限操作此订单")

    if order.status != "pending":
        raise BadRequestError(f"订单状态为 '{order.status}'，无法支付")

    now = datetime.now(timezone.utc)
    if order.expires_at and order.expires_at < now:
        # 超时订单就地关闭，避免重复关闭 Celery 任务也会执行
        order.status = "closed"
        db.add(order)
        raise BadRequestError("订单已过期，请重新下单")

    # 计算买家余额
    buyer_balance = await _calc_user_balance(current_user.id, db)
    if buyer_balance < order.paid_amount:
        raise BadRequestError(
            f"余额不足（当前余额 {buyer_balance} 元，订单金额 {order.paid_amount} 元）"
        )

    # 买家扣款流水
    buyer_tx = Transaction(
        id=uuid.uuid4(),
        tx_no=_new_tx_no(),
        order_id=order.id,
        user_id=current_user.id,
        type="payment",
        direction="out",
        amount=order.paid_amount,
        balance_before=buyer_balance,
        balance_after=buyer_balance - order.paid_amount,
        payment_method="balance",
        status="completed",
        description=f"购买插件：{order.plugin_snapshot.get('name', '')}",
    )
    db.add(buyer_tx)

    # 更新订单
    order.status = "paid"
    order.paid_at = now
    order.payment_method = "balance"
    order.payment_channel = "balance"
    db.add(order)

    # 写入已购记录
    purchase = UserPurchase(
        id=uuid.uuid4(),
        user_id=current_user.id,
        plugin_id=order.plugin_id,
        order_id=order.id,
    )
    db.add(purchase)

    # 开发者入账流水
    dev_balance = await _calc_user_balance(order.developer_id, db)
    dev_tx = Transaction(
        id=uuid.uuid4(),
        tx_no=_new_tx_no(),
        order_id=order.id,
        user_id=order.developer_id,
        type="settlement",
        direction="in",
        amount=order.developer_revenue,
        balance_before=dev_balance,
        balance_after=dev_balance + order.developer_revenue,
        payment_method="balance",
        status="completed",
        description=f"插件销售收入：{order.plugin_snapshot.get('name', '')}",
    )
    db.add(dev_tx)

    return Response.ok(data=_to_order_response(order), message="支付成功")
