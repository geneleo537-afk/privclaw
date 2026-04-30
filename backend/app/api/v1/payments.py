"""
支付端点：支付宝发起支付、异步回调通知处理。

POST /orders/{order_id}/pay/alipay — 发起支付宝支付，返回二维码 URL
POST /payments/alipay/notify       — 支付宝异步回调（无需登录，支付宝服务器主动推送）
POST /orders/{order_id}/pay/dev-complete — 本地开发时手动完成支付
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import case as sa_case, func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.order import Order, UserPurchase
from app.models.user import User
from app.models.wallet import Transaction
from app.schemas.common import Response

router = APIRouter()


def _new_tx_no() -> str:
    """生成唯一交易流水号：TX + 时间戳(14位) + UUID 前 8 位。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TX{ts}{uuid.uuid4().hex[:8]}"


def _get_alipay_provider():
    """惰性导入支付宝 Provider，避免 SDK 导入失败直接拖垮整个服务。"""
    from app.services.payment.alipay import AlipayProvider

    return AlipayProvider()


async def _calc_user_balance(user_id: uuid.UUID, db: AsyncSession) -> Decimal:
    """计算用户账户余额（completed 流水的累计入账 - 累计出账）。"""
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


async def _complete_order_payment(
    order: Order,
    channel_trade_no: str,
    pay_channel: str,
    db: AsyncSession,
) -> None:
    """
    订单支付完成后的统一处理逻辑（供余额支付和回调通知复用）。

    执行步骤：
    1. 更新订单状态为 paid，记录第三方流水号
    2. 写入 user_purchases 记录
    3. 写入开发者入账流水（Transaction，direction='in'）
    """
    now = datetime.now(timezone.utc)

    order.status = "paid"
    order.paid_at = now
    order.payment_method = pay_channel
    order.payment_channel = pay_channel
    order.third_party_tx_id = channel_trade_no
    db.add(order)

    # 幂等检查：避免重复写入已购记录
    existing = await db.execute(
        select(UserPurchase).where(
            UserPurchase.user_id == order.buyer_id,
            UserPurchase.plugin_id == order.plugin_id,
        )
    )
    if existing.scalar_one_or_none() is None:
        purchase = UserPurchase(
            id=uuid.uuid4(),
            user_id=order.buyer_id,
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
        payment_method=pay_channel,
        third_party_tx_id=channel_trade_no,
        status="completed",
        description=f"插件销售收入：{order.plugin_snapshot.get('name', '')}",
    )
    db.add(dev_tx)


@router.post(
    "/orders/{order_id}/pay/alipay",
    response_model=Response[dict],
    summary="发起支付宝支付",
)
async def pay_alipay(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    为指定订单发起支付宝扫码支付，返回二维码 URL 供前端展示。
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if order.buyer_id != current_user.id:
        raise ForbiddenError("无权限操作此订单")

    if order.status != "pending":
        raise BadRequestError(f"订单状态为 '{order.status}'，无法发起支付")

    try:
        provider = _get_alipay_provider()
        payment_result = await provider.create_payment(
            order_no=order.order_no,
            amount=order.paid_amount,
            subject=order.plugin_snapshot.get("name", "插件购买"),
        )
        if not payment_result.success:
            raise BadRequestError(payment_result.error or "支付宝下单失败")
        qr_code_url = payment_result.qr_code_url
        note = ""
    except Exception as exc:
        if settings.APP_ENV != "development":
            raise
        qr_code_url = ""
        note = f"支付宝 SDK 当前不可用，请改用本地模拟支付。{exc}"

    return Response.ok(
        data={
            "order_id": str(order.id),
            "order_no": order.order_no,
            "amount": str(order.paid_amount),
            "qr_code_url": qr_code_url,
            "note": note,
        }
    )


@router.post(
    "/orders/{order_id}/pay/dev-complete",
    response_model=Response[dict],
    summary="本地开发：手动完成支付",
)
async def dev_complete_payment(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    本地开发辅助接口。

    由于支付宝异步回调无法直接回调到 localhost，本接口允许在开发环境
    手动将待支付订单标记为已支付，用于联调购买、已购列表、下载授权等流程。
    """
    if settings.APP_ENV == "production":
        raise NotFoundError("生产环境不存在该接口")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()
    if order is None:
        raise NotFoundError("订单不存在")
    if order.buyer_id != current_user.id:
        raise ForbiddenError("无权限操作此订单")
    if order.status != "pending":
        raise BadRequestError(f"订单状态为 '{order.status}'，无法模拟支付")

    await _complete_order_payment(
        order=order,
        channel_trade_no=f"DEV-{uuid.uuid4().hex[:12]}",
        pay_channel="alipay",
        db=db,
    )
    return Response.ok(
        data={
            "order_id": str(order.id),
            "order_no": order.order_no,
            "status": "paid",
        },
        message="本地模拟支付成功",
    )


@router.post(
    "/payments/alipay/notify",
    summary="支付宝异步回调通知",
    # 此端点无需 JWT 鉴权，支付宝服务器主动推送
    # 返回纯文本 "success" 或 "fail"
)
async def alipay_notify(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    接收支付宝服务器的异步支付结果通知。

    安全要求：
    - 必须验证支付宝签名（RSA2），防止伪造通知
    - 幂等处理：同一 trade_no 重复通知只处理一次
    - 必须在 5 秒内响应，否则支付宝会重试
    - 响应体必须为纯文本 "success"（成功）或 "fail"（失败需重试）

    当前实现：AlipayProvider 尚未实现签名验证，所有通知直接返回 "fail"，
    接入支付宝 SDK 后替换 TODO 注释块即可。
    """
    try:
        form_data = dict(await request.form())
        provider = _get_alipay_provider()
        verify_result = provider.verify_callback(form_data)
        if not verify_result.success:
            return PlainTextResponse("fail")

        order_result = await db.execute(
            select(Order).where(Order.order_no == verify_result.order_no)
        )
        order = order_result.scalar_one_or_none()
        if order is None:
            return PlainTextResponse("fail")
        if order.status == "paid":
            return PlainTextResponse("success")
        if order.status != "pending":
            return PlainTextResponse("fail")
        if verify_result.paid_amount != order.paid_amount:
            return PlainTextResponse("fail")

        await _complete_order_payment(
            order=order,
            channel_trade_no=verify_result.trade_no,
            pay_channel="alipay",
            db=db,
        )
        return PlainTextResponse("success")

    except Exception:
        return PlainTextResponse("fail")
