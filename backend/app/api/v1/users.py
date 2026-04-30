"""
用户端点：个人信息、成为开发者、已购列表、订单列表、收益统计。

GET  /users/me                 — 获取当前用户信息
PUT  /users/me                 — 更新个人资料
POST /users/me/become-developer — 申请开发者身份
GET  /users/me/purchases       — 我的已购插件（分页）
GET  /users/me/orders          — 我的订单列表（分页）
GET  /users/me/revenue         — 开发者收益统计（仅开发者）
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_developer
from app.core.exceptions import BadRequestError, ConflictError
from app.models.order import Order, UserPurchase
from app.models.plugin import Plugin
from app.models.user import User, UserProfile
from app.schemas.common import PageData, PageResponse, Response
from app.schemas.user import UpdateProfileRequest, UserDetailResponse, UserResponse

router = APIRouter()


@router.get(
    "/users/me",
    response_model=Response[UserDetailResponse],
    summary="获取当前用户详情",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[UserDetailResponse]:
    """
    返回当前登录用户的完整个人信息，包含扩展资料（bio、website 等）。
    扩展资料从 UserProfile 关联表中读取，若不存在则返回空字符串。
    """
    # 加载用户扩展资料
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile: Optional[UserProfile] = profile_result.scalar_one_or_none()

    response_data = UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        status=current_user.status,
        email_verified=current_user.email_verified,
        is_developer=current_user.is_developer,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
        bio=profile.bio if profile else None,
        website=profile.website if profile else None,
        github_url=profile.github_url if profile else None,
        company=profile.company if profile else None,
    )
    return Response.ok(data=response_data)


@router.put(
    "/users/me",
    response_model=Response[UserDetailResponse],
    summary="更新个人资料",
)
async def update_me(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[UserDetailResponse]:
    """
    更新当前用户的个人资料。

    - User 表：nickname、avatar_url
    - UserProfile 表：bio、website、github_url、company
    - 仅更新请求体中提供（非 None）的字段，未提供的字段保持原值不变
    """
    # 更新 User 主表字段
    if req.nickname is not None:
        current_user.nickname = req.nickname
    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url
    db.add(current_user)

    # 更新或创建 UserProfile 扩展资料
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile: Optional[UserProfile] = profile_result.scalar_one_or_none()

    if profile is None:
        profile = UserProfile(id=uuid.uuid4(), user_id=current_user.id)
        db.add(profile)

    if req.bio is not None:
        profile.bio = req.bio
    if req.website is not None:
        profile.website = req.website
    if req.github_url is not None:
        profile.github_url = req.github_url
    if req.company is not None:
        profile.company = req.company

    # 事务由 get_db 依赖统一提交
    response_data = UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        status=current_user.status,
        email_verified=current_user.email_verified,
        is_developer=current_user.is_developer,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
        bio=profile.bio,
        website=profile.website,
        github_url=profile.github_url,
        company=profile.company,
    )
    return Response.ok(data=response_data, message="资料更新成功")


@router.post(
    "/users/me/become-developer",
    response_model=Response[UserResponse],
    summary="申请开发者身份",
)
async def become_developer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[UserResponse]:
    """
    将当前用户角色从 buyer 升级为 developer。

    - 已是 developer 或 admin 的用户重复请求时返回 409 Conflict
    - 升级后 is_developer 标志同步设为 True
    """
    if current_user.role in ("developer", "admin"):
        raise ConflictError("已拥有开发者身份，无需重复申请")

    current_user.role = "developer"
    current_user.is_developer = True
    db.add(current_user)

    return Response.ok(
        data=UserResponse.model_validate(current_user),
        message="已成功开通开发者身份",
    )


@router.get(
    "/users/me/purchases",
    response_model=PageResponse[dict],
    summary="我的已购插件列表",
)
async def get_my_purchases(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    分页查询当前用户的已购插件列表。

    关联 user_purchases 和 plugins 两张表，返回插件基础信息和购买时间。
    """
    offset = (page - 1) * page_size

    # 统计总数
    count_result = await db.execute(
        select(func.count()).where(UserPurchase.user_id == current_user.id)
    )
    total: int = count_result.scalar_one()

    # 分页查询购买记录，关联插件信息
    purchase_result = await db.execute(
        select(UserPurchase, Plugin)
        .join(Plugin, Plugin.id == UserPurchase.plugin_id)
        .where(UserPurchase.user_id == current_user.id)
        .order_by(UserPurchase.purchased_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = purchase_result.all()

    items = [
        {
            "purchase_id": str(row.UserPurchase.id),
            "plugin_id": str(row.Plugin.id),
            "plugin_name": row.Plugin.name,
            "plugin_slug": row.Plugin.slug,
            "plugin_icon_url": row.Plugin.icon_url,
            "plugin_version": row.Plugin.current_version,
            "purchased_at": row.UserPurchase.purchased_at.isoformat(),
        }
        for row in rows
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.get(
    "/users/me/orders",
    response_model=PageResponse[dict],
    summary="我的订单列表",
)
async def get_my_orders(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[dict]:
    """
    分页查询当前用户的订单列表，按创建时间倒序排列。
    """
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count()).where(Order.buyer_id == current_user.id)
    )
    total: int = count_result.scalar_one()

    order_result = await db.execute(
        select(Order)
        .where(Order.buyer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = order_result.scalars().all()

    items = [
        {
            "id": str(o.id),
            "order_no": o.order_no,
            "plugin_snapshot": o.plugin_snapshot,
            "paid_amount": str(o.paid_amount),
            "status": o.status,
            "payment_method": o.payment_method,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            "expires_at": o.expires_at.isoformat() if o.expires_at else None,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.get(
    "/users/me/revenue",
    response_model=Response[dict],
    summary="开发者收益统计",
)
async def get_my_revenue(
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    查询当前开发者的收益统计：今日收益、本月收益、累计收益。

    - 仅统计 status='paid' 的订单中 developer_revenue 字段
    - 今日：按 UTC+8 当天 00:00:00 起算
    - 本月：按 UTC+8 当月第一天起算
    """
    now_utc = datetime.now(timezone.utc)

    # 今日收益（UTC，数据库统一使用 UTC 存储）
    today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.coalesce(func.sum(Order.developer_revenue), Decimal("0.00")))
        .where(Order.developer_id == current_user.id)
        .where(Order.status == "paid")
        .where(Order.paid_at >= today_start)
    )
    today_revenue: Decimal = today_result.scalar_one()

    # 本月收益
    month_start = now_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.coalesce(func.sum(Order.developer_revenue), Decimal("0.00")))
        .where(Order.developer_id == current_user.id)
        .where(Order.status == "paid")
        .where(Order.paid_at >= month_start)
    )
    month_revenue: Decimal = month_result.scalar_one()

    # 累计收益
    total_result = await db.execute(
        select(func.coalesce(func.sum(Order.developer_revenue), Decimal("0.00")))
        .where(Order.developer_id == current_user.id)
        .where(Order.status == "paid")
    )
    total_revenue: Decimal = total_result.scalar_one()

    # 累计订单数
    order_count_result = await db.execute(
        select(func.count())
        .where(Order.developer_id == current_user.id)
        .where(Order.status == "paid")
    )
    total_orders: int = order_count_result.scalar_one()

    return Response.ok(
        data={
            "today_revenue": str(today_revenue),
            "month_revenue": str(month_revenue),
            "total_revenue": str(total_revenue),
            "total_orders": total_orders,
        }
    )


@router.get(
    "/users/me/stats/trend",
    response_model=Response[dict],
    summary="开发者收入趋势",
)
async def get_my_trend(
    days: int = Query(30, ge=1, le=90, description="近 N 天"),
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    查询当前开发者近 N 天的收入/销量趋势，按 paid_at 日期分组。
    无数据的天自动补零，保证返回完整日期序列。
    """
    from datetime import timedelta

    now_utc = datetime.now(timezone.utc)
    start_date = (now_utc - timedelta(days=days - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    stats = await db.execute(
        select(
            func.cast(Order.paid_at, func.DATE).label("d"),
            func.count().label("cnt"),
            func.coalesce(func.sum(Order.developer_revenue), Decimal("0.00")).label("rev"),
        )
        .where(
            Order.developer_id == current_user.id,
            Order.status == "paid",
            Order.paid_at >= start_date,
        )
        .group_by("d")
    )
    data_map: dict[str, tuple[int, float]] = {}
    for row in stats.all():
        data_map[str(row.d)] = (row.cnt, float(row.rev))

    points = []
    for i in range(days):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        cnt, rev = data_map.get(date_str, (0, 0.0))
        points.append({
            "date": date_str,
            "sales_count": cnt,
            "revenue": round(rev, 2),
        })

    return Response.ok(data={"points": points})
