"""
管理后台端点（仅限 admin 角色）。

GET  /admin/dashboard                         — 平台运营数据仪表盘
GET  /admin/plugins                           — 插件列表（支持状态过滤）
PUT  /admin/plugins/{plugin_id}/status        — 变更插件状态
GET  /admin/orders                            — 订单列表
POST /admin/orders/{order_id}/refund          — 退款处理
GET  /admin/withdrawals                       — 提现申请列表（支持状态过滤）
POST /admin/withdrawals/{withdrawal_id}/approve — 批准提现
POST /admin/withdrawals/{withdrawal_id}/reject  — 拒绝提现并退还余额
GET  /admin/users                             — 用户列表
PUT  /admin/users/{user_id}/ban               — 封禁/解封用户
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, case as sa_case, func as sa_func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.order import Order
from app.models.plugin import Plugin
from app.models.user import User
from app.models.wallet import Settlement, Transaction
from app.schemas.admin import (
    ApproveWithdrawalRequest,
    BanUserRequest,
    DashboardResponse,
    RefundOrderRequest,
    RejectWithdrawalRequest,
    TrendDataPoint,
    TrendResponse,
    UpdatePluginStatusRequest,
)
from app.schemas.common import PageData, PageResponse, Response

router = APIRouter(prefix="/admin")

# 合法的插件状态集合（管理员可操作的范围）
VALID_PLUGIN_STATUSES = {"published", "suspended", "draft", "removed"}
# 合法的用户封禁操作
VALID_BAN_ACTIONS = {"ban", "unban"}


def _new_tx_no() -> str:
    """生成唯一交易流水号：TX + 时间戳(14位) + UUID 前 8 位。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TX{ts}{uuid.uuid4().hex[:8]}"


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


@router.get(
    "/dashboard",
    response_model=Response[DashboardResponse],
    summary="平台运营仪表盘",
)
async def dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[DashboardResponse]:
    """
    查询平台核心运营指标：
    - 注册用户总数（软删除用户不计入）
    - 已发布插件总数
    - 所有订单总数
    - 平台累计收入（platform_fee 之和，status='paid'）
    - 待审核提现申请数量
    """
    # 用户总数
    users_result = await db.execute(
        select(sa_func.count()).select_from(User).where(User.deleted_at.is_(None))
    )
    total_users: int = users_result.scalar_one()

    # 已发布插件总数
    plugins_result = await db.execute(
        select(sa_func.count())
        .select_from(Plugin)
        .where(Plugin.status == "published", Plugin.deleted_at.is_(None))
    )
    total_plugins: int = plugins_result.scalar_one()

    # 订单总数
    orders_result = await db.execute(select(sa_func.count()).select_from(Order))
    total_orders: int = orders_result.scalar_one()

    # 平台累计收入
    revenue_result = await db.execute(
        select(
            sa_func.coalesce(sa_func.sum(Order.platform_fee), Decimal("0.00"))
        ).where(Order.status == "paid")
    )
    total_revenue: Decimal = revenue_result.scalar_one() or Decimal("0.00")

    # 待审核提现申请数
    pending_wd_result = await db.execute(
        select(sa_func.count())
        .select_from(Settlement)
        .where(Settlement.status == "pending")
    )
    pending_withdrawals: int = pending_wd_result.scalar_one()

    # 今日维度
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    today_orders_result = await db.execute(
        select(sa_func.count())
        .select_from(Order)
        .where(Order.status == "paid", Order.paid_at >= today_start)
    )
    today_orders: int = today_orders_result.scalar_one()

    today_revenue_result = await db.execute(
        select(
            sa_func.coalesce(sa_func.sum(Order.platform_fee), Decimal("0.00"))
        ).where(Order.status == "paid", Order.paid_at >= today_start)
    )
    today_revenue: Decimal = today_revenue_result.scalar_one() or Decimal("0.00")

    today_users_result = await db.execute(
        select(sa_func.count())
        .select_from(User)
        .where(User.deleted_at.is_(None), User.created_at >= today_start)
    )
    today_new_users: int = today_users_result.scalar_one()

    # 待审核插件数
    pending_reviews_result = await db.execute(
        select(sa_func.count())
        .select_from(Plugin)
        .where(Plugin.deleted_at.is_(None), Plugin.status == "draft")
    )
    pending_reviews: int = pending_reviews_result.scalar_one()

    return Response.ok(
        data=DashboardResponse(
            total_users=total_users,
            total_plugins=total_plugins,
            total_orders=total_orders,
            total_revenue=float(total_revenue),
            pending_withdrawals=pending_withdrawals,
            today_orders=today_orders,
            today_revenue=float(today_revenue),
            today_new_users=today_new_users,
            pending_reviews=pending_reviews,
        )
    )


@router.get(
    "/stats/trend",
    response_model=Response[TrendResponse],
    summary="平台趋势数据",
)
async def admin_trend(
    days: int = Query(30, ge=1, le=90, description="近 N 天"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[TrendResponse]:
    """
    按天统计近 N 天的订单数、收入、新增用户。
    无数据的天自动补零，保证返回完整日期序列。
    """
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=days - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # 订单 + 收入（按 paid_at 日期分组）
    order_stats = await db.execute(
        select(
            sa_func.cast(Order.paid_at, sa_func.DATE).label("d"),
            sa_func.count().label("cnt"),
            sa_func.coalesce(sa_func.sum(Order.platform_fee), Decimal("0.00")).label("rev"),
        )
        .where(Order.status == "paid", Order.paid_at >= start_date)
        .group_by("d")
    )
    order_map: dict[str, tuple[int, float]] = {}
    for row in order_stats.all():
        order_map[str(row.d)] = (row.cnt, float(row.rev))

    # 新增用户（按 created_at 日期分组）
    user_stats = await db.execute(
        select(
            sa_func.cast(User.created_at, sa_func.DATE).label("d"),
            sa_func.count().label("cnt"),
        )
        .where(User.deleted_at.is_(None), User.created_at >= start_date)
        .group_by("d")
    )
    user_map: dict[str, int] = {}
    for row in user_stats.all():
        user_map[str(row.d)] = row.cnt

    # 合并成完整日期序列
    points = []
    for i in range(days):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        oc, rev = order_map.get(date_str, (0, 0.0))
        nu = user_map.get(date_str, 0)
        points.append(TrendDataPoint(
            date=date_str,
            order_count=oc,
            revenue=round(rev, 2),
            new_users=nu,
        ))

    return Response.ok(data=TrendResponse(points=points))


@router.get(
    "/plugins",
    response_model=PageResponse[dict],
    summary="管理插件列表",
)
async def admin_list_plugins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="按状态过滤：draft/published/suspended/removed"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    管理员查询所有插件（含各状态），支持按状态过滤，按创建时间倒序排列。
    """
    offset = (page - 1) * page_size
    conditions = [Plugin.deleted_at.is_(None)]
    if status:
        conditions.append(Plugin.status == status)

    count_result = await db.execute(
        select(sa_func.count()).select_from(Plugin).where(and_(*conditions))
    )
    total: int = count_result.scalar_one()

    plugin_result = await db.execute(
        select(Plugin)
        .where(and_(*conditions))
        .order_by(Plugin.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    plugins = plugin_result.scalars().all()

    items = [
        {
            "id": str(p.id),
            "name": p.name,
            "slug": p.slug,
            "status": p.status,
            "review_status": p.review_status,
            "developer_id": str(p.developer_id),
            "price": str(p.price),
            "is_free": p.is_free,
            "download_count": p.download_count,
            "purchase_count": p.purchase_count,
            "created_at": p.created_at.isoformat(),
        }
        for p in plugins
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.put(
    "/plugins/{plugin_id}/status",
    response_model=Response[dict],
    summary="变更插件状态",
)
async def update_plugin_status(
    plugin_id: uuid.UUID,
    req: UpdatePluginStatusRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    管理员变更插件状态（发布/下架/回归草稿/移除）。

    合法目标状态：published、suspended、draft、removed。
    变更为 published 时，若 published_at 为空则自动填充当前时间。
    """
    if req.status not in VALID_PLUGIN_STATUSES:
        raise BadRequestError(
            f"无效的插件状态：{req.status}，合法值：{', '.join(VALID_PLUGIN_STATUSES)}"
        )

    result = await db.execute(
        select(Plugin).where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()
    if plugin is None:
        raise NotFoundError("插件不存在")

    plugin.status = req.status
    if req.status == "published" and plugin.published_at is None:
        plugin.published_at = datetime.now(timezone.utc)
    if req.reason:
        plugin.review_note = req.reason

    db.add(plugin)

    return Response.ok(
        data={
            "plugin_id": str(plugin.id),
            "new_status": req.status,
            "reason": req.reason,
        },
        message=f"插件状态已更新为 {req.status}",
    )


@router.get(
    "/orders",
    response_model=PageResponse[dict],
    summary="管理订单列表",
)
async def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="按状态过滤"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    管理员查询所有订单，支持按状态过滤，按创建时间倒序排列。
    """
    offset = (page - 1) * page_size
    conditions = []
    if status:
        conditions.append(Order.status == status)

    count_result = await db.execute(
        select(sa_func.count()).select_from(Order).where(and_(*conditions))
        if conditions
        else select(sa_func.count()).select_from(Order)
    )
    total: int = count_result.scalar_one()

    order_result = await db.execute(
        select(Order)
        .where(and_(*conditions))
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = order_result.scalars().all()

    items = [
        {
            "id": str(o.id),
            "order_no": o.order_no,
            "buyer_id": str(o.buyer_id),
            "developer_id": str(o.developer_id),
            "paid_amount": str(o.paid_amount),
            "platform_fee": str(o.platform_fee),
            "developer_revenue": str(o.developer_revenue),
            "status": o.status,
            "payment_method": o.payment_method,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            "created_at": o.created_at.isoformat(),
            "plugin_name": o.plugin_snapshot.get("name", ""),
        }
        for o in orders
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.post(
    "/orders/{order_id}/refund",
    response_model=Response[dict],
    summary="订单退款",
)
async def admin_refund(
    order_id: uuid.UUID,
    req: RefundOrderRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    管理员对已支付订单发起退款。

    退款流程：
    1. 验证订单为 paid 状态
    2. 将订单状态变更为 refunded
    3. 从开发者余额中扣除对应收益（Transaction direction='out', type='refund'）
    4. 买家退款流水（direction='in', type='refund'）
    5. 删除 user_purchases 记录（退款后撤销下载权限）

    注意：第三方支付（支付宝）实际退款需调用 AlipayProvider.refund()，
    当前版本仅更新数据库状态，对接支付宝后补充实际退款调用。
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order: Optional[Order] = result.scalar_one_or_none()

    if order is None:
        raise NotFoundError("订单不存在")

    if order.status != "paid":
        raise BadRequestError(f"订单状态为 '{order.status}'，仅 paid 状态可退款")

    now = datetime.now(timezone.utc)

    # 更新订单状态
    order.status = "refunded"
    order.refunded_at = now
    db.add(order)

    # 扣除开发者已入账收益
    dev_balance = await _calc_user_balance(order.developer_id, db)
    deduct_amount = min(order.developer_revenue, dev_balance)  # 不能扣为负
    if deduct_amount > Decimal("0.00"):
        dev_deduct_tx = Transaction(
            id=uuid.uuid4(),
            tx_no=_new_tx_no(),
            order_id=order.id,
            user_id=order.developer_id,
            type="refund",
            direction="out",
            amount=deduct_amount,
            balance_before=dev_balance,
            balance_after=dev_balance - deduct_amount,
            status="completed",
            description=f"退款扣除：订单 {order.order_no}，原因：{req.reason}",
        )
        db.add(dev_deduct_tx)

    # 买家退款入账
    buyer_balance = await _calc_user_balance(order.buyer_id, db)
    buyer_refund_tx = Transaction(
        id=uuid.uuid4(),
        tx_no=_new_tx_no(),
        order_id=order.id,
        user_id=order.buyer_id,
        type="refund",
        direction="in",
        amount=order.paid_amount,
        balance_before=buyer_balance,
        balance_after=buyer_balance + order.paid_amount,
        status="completed",
        description=f"订单退款：{order.plugin_snapshot.get('name', '')}，原因：{req.reason}",
    )
    db.add(buyer_refund_tx)

    # 删除已购记录（撤销下载权限）
    from app.models.order import UserPurchase
    purchase_result = await db.execute(
        select(UserPurchase).where(
            UserPurchase.user_id == order.buyer_id,
            UserPurchase.plugin_id == order.plugin_id,
        )
    )
    purchase = purchase_result.scalar_one_or_none()
    if purchase:
        await db.delete(purchase)

    return Response.ok(
        data={
            "order_id": str(order.id),
            "order_no": order.order_no,
            "refund_amount": str(order.paid_amount),
            "status": "refunded",
        },
        message="退款处理成功",
    )


@router.get(
    "/withdrawals",
    response_model=PageResponse[dict],
    summary="提现申请列表",
)
async def admin_list_withdrawals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="按状态过滤：pending/processing/completed/cancelled"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    管理员查询所有提现申请，支持按状态过滤，按申请时间倒序排列。
    """
    offset = (page - 1) * page_size
    conditions = []
    if status:
        conditions.append(Settlement.status == status)

    count_result = await db.execute(
        select(sa_func.count()).select_from(Settlement).where(and_(*conditions))
        if conditions
        else select(sa_func.count()).select_from(Settlement)
    )
    total: int = count_result.scalar_one()

    settlement_result = await db.execute(
        select(Settlement)
        .where(and_(*conditions))
        .order_by(Settlement.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    settlements = settlement_result.scalars().all()

    items = [
        {
            "id": str(s.id),
            "settlement_no": s.settlement_no,
            "developer_id": str(s.developer_id),
            "amount": str(s.final_amount),
            "withdrawal_method": s.withdrawal_method,
            "withdrawal_account": s.withdrawal_account,
            "status": s.status,
            "requested_at": s.created_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "failure_reason": s.failure_reason or None,
        }
        for s in settlements
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.post(
    "/withdrawals/{withdrawal_id}/approve",
    response_model=Response[dict],
    summary="批准提现申请",
)
async def approve_withdrawal(
    withdrawal_id: uuid.UUID,
    req: ApproveWithdrawalRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    管理员批准提现申请，将 Settlement 状态变更为 completed，
    并写入开发者出账流水（Transaction direction='out', type='withdrawal'）。

    注意：实际打款操作需在系统外部（如支付宝批量转账）完成，
    此接口仅更新系统内状态，确认打款已执行后再调用。
    """
    result = await db.execute(select(Settlement).where(Settlement.id == withdrawal_id))
    settlement: Optional[Settlement] = result.scalar_one_or_none()

    if settlement is None:
        raise NotFoundError("提现申请不存在")

    if settlement.status not in ("pending", "processing"):
        raise BadRequestError(f"提现申请状态为 '{settlement.status}'，无法批准")

    now = datetime.now(timezone.utc)
    settlement.status = "completed"
    settlement.completed_at = now
    if req.note:
        settlement.failure_reason = f"[批准备注] {req.note}"
    db.add(settlement)

    # 校验余额充足性（退款场景可能导致余额缩水）
    dev_balance = await _calc_user_balance(settlement.developer_id, db)
    if dev_balance < settlement.final_amount:
        raise BadRequestError(
            f"开发者余额不足（当前余额 {dev_balance} 元，提现金额 {settlement.final_amount} 元），"
            "请先处理退款问题后再审批"
        )

    # 写入开发者提现出账流水
    withdrawal_tx = Transaction(
        id=uuid.uuid4(),
        tx_no=_new_tx_no(),
        user_id=settlement.developer_id,
        type="withdrawal",
        direction="out",
        amount=settlement.final_amount,
        balance_before=dev_balance,
        balance_after=dev_balance - settlement.final_amount,
        payment_method=settlement.withdrawal_method,
        status="completed",
        description=f"提现结算：{settlement.settlement_no}",
    )
    db.add(withdrawal_tx)

    return Response.ok(
        data={
            "withdrawal_id": str(settlement.id),
            "settlement_no": settlement.settlement_no,
            "amount": str(settlement.final_amount),
            "status": "completed",
            "completed_at": now.isoformat(),
        },
        message="提现申请已批准",
    )


@router.post(
    "/withdrawals/{withdrawal_id}/reject",
    response_model=Response[dict],
    summary="拒绝提现申请",
)
async def reject_withdrawal(
    withdrawal_id: uuid.UUID,
    req: RejectWithdrawalRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    管理员拒绝提现申请，将 Settlement 状态变更为 cancelled，
    并写入开发者退还入账流水（余额归还，防止资金丢失）。

    拒绝时必须填写原因（reason 字段），方便开发者了解拒绝理由。
    """
    result = await db.execute(select(Settlement).where(Settlement.id == withdrawal_id))
    settlement: Optional[Settlement] = result.scalar_one_or_none()

    if settlement is None:
        raise NotFoundError("提现申请不存在")

    if settlement.status not in ("pending", "processing"):
        raise BadRequestError(f"提现申请状态为 '{settlement.status}'，无法拒绝")

    now = datetime.now(timezone.utc)
    settlement.status = "cancelled"
    settlement.failure_reason = req.reason
    db.add(settlement)

    # pending/processing 阶段拒绝：资金从未实际转出，无需写对冲流水。
    # 拒绝原因已记录在 settlement.failure_reason，满足审计需求。

    return Response.ok(
        data={
            "withdrawal_id": str(settlement.id),
            "settlement_no": settlement.settlement_no,
            "status": "cancelled",
            "reason": req.reason,
        },
        message="提现申请已拒绝",
    )


@router.get(
    "/users",
    response_model=PageResponse[dict],
    summary="用户列表",
)
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None, description="按角色过滤：buyer/developer/admin"),
    status: Optional[str] = Query(None, description="按状态过滤：active/suspended/banned"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    管理员查询所有用户，支持按角色和状态过滤，按注册时间倒序排列。
    """
    offset = (page - 1) * page_size
    conditions = [User.deleted_at.is_(None)]
    if role:
        conditions.append(User.role == role)
    if status:
        conditions.append(User.status == status)

    count_result = await db.execute(
        select(sa_func.count()).select_from(User).where(and_(*conditions))
    )
    total: int = count_result.scalar_one()

    user_result = await db.execute(
        select(User)
        .where(and_(*conditions))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    users = user_result.scalars().all()

    items = [
        {
            "id": str(u.id),
            "nickname": u.nickname,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "is_developer": u.is_developer,
            "email_verified": u.email_verified,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.put(
    "/users/{user_id}/ban",
    response_model=Response[dict],
    summary="封禁/解封用户",
)
async def ban_user(
    user_id: uuid.UUID,
    req: BanUserRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    管理员封禁或解封用户账号。

    - action='ban'：将 status 设为 'banned'，用户无法登录
    - action='unban'：将 status 恢复为 'active'
    - 不允许封禁管理员账号（防止误操作锁定所有管理员）
    """
    if req.action not in VALID_BAN_ACTIONS:
        raise BadRequestError(f"无效的操作：{req.action}，合法值：ban / unban")

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user: Optional[User] = result.scalar_one_or_none()

    if user is None:
        raise NotFoundError("用户不存在")

    if user.role == "admin":
        raise BadRequestError("不允许封禁管理员账号")

    if user.id == current_user.id:
        raise BadRequestError("不允许封禁当前登录的管理员账号")

    if req.action == "ban":
        user.status = "banned"
        msg = f"用户 {user.nickname} 已被封禁"
    else:
        user.status = "active"
        msg = f"用户 {user.nickname} 已解封"

    db.add(user)

    return Response.ok(
        data={
            "user_id": str(user.id),
            "nickname": user.nickname,
            "action": req.action,
            "new_status": user.status,
            "reason": req.reason,
        },
        message=msg,
    )
