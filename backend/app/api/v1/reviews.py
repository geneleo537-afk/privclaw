"""
插件评价端点。

GET    /plugins/{plugin_id}/reviews          — 评价分页列表（公开）
GET    /plugins/{plugin_id}/reviews/summary  — 评价汇总（公开）
POST   /plugins/{plugin_id}/reviews          — 发表评价（需登录+已购）
DELETE /plugins/{plugin_id}/reviews/{review_id} — 删除评价（仅作者）
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func as sa_func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_optional_user
from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.order import UserPurchase
from app.models.plugin import Plugin
from app.models.review import PluginReview
from app.models.user import User
from app.schemas.common import PageData, PageResponse, Response
from app.schemas.review import CreateReviewRequest, ReviewResponse, ReviewSummary

router = APIRouter()


async def _sync_plugin_rating(plugin_id: uuid.UUID, db: AsyncSession) -> None:
    """同步更新插件冗余评分字段（在同一事务中调用）。"""
    stats = await db.execute(
        select(
            sa_func.coalesce(sa_func.avg(PluginReview.rating), Decimal("0.00")),
            sa_func.count(),
        )
        .where(
            PluginReview.plugin_id == plugin_id,
            PluginReview.deleted_at.is_(None),
            PluginReview.is_visible.is_(True),
        )
    )
    avg_rating, rating_count = stats.one()
    await db.execute(
        update(Plugin)
        .where(Plugin.id == plugin_id)
        .values(avg_rating=round(float(avg_rating), 2), rating_count=rating_count)
    )


@router.get(
    "/plugins/{plugin_id}/reviews",
    response_model=PageResponse[ReviewResponse],
    summary="插件评价列表",
)
async def list_reviews(
    plugin_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[ReviewResponse]:
    """公开接口：分页查询插件的可见评价，关联用户昵称和头像。"""
    conditions = [
        PluginReview.plugin_id == plugin_id,
        PluginReview.deleted_at.is_(None),
        PluginReview.is_visible.is_(True),
    ]
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(sa_func.count())
        .select_from(PluginReview)
        .where(and_(*conditions))
    )
    total: int = count_result.scalar_one()

    rows = await db.execute(
        select(PluginReview, User.nickname, User.avatar_url)
        .join(User, User.id == PluginReview.user_id)
        .where(and_(*conditions))
        .order_by(PluginReview.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    items = [
        ReviewResponse(
            id=review.id,
            plugin_id=review.plugin_id,
            user_id=review.user_id,
            order_id=review.order_id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_visible=review.is_visible,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_nickname=nickname,
            user_avatar_url=avatar_url or "",
        )
        for review, nickname, avatar_url in rows.all()
    ]

    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.get(
    "/plugins/{plugin_id}/reviews/summary",
    response_model=Response[ReviewSummary],
    summary="评价汇总",
)
async def review_summary(
    plugin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response[ReviewSummary]:
    """公开接口：查询插件的评分汇总（平均分+各星级分布）。"""
    conditions = [
        PluginReview.plugin_id == plugin_id,
        PluginReview.deleted_at.is_(None),
        PluginReview.is_visible.is_(True),
    ]

    # 平均分和总数
    agg_result = await db.execute(
        select(
            sa_func.coalesce(sa_func.avg(PluginReview.rating), 0.0),
            sa_func.count(),
        )
        .where(and_(*conditions))
    )
    avg_rating, rating_count = agg_result.one()

    # 各星级分布
    dist_result = await db.execute(
        select(PluginReview.rating, sa_func.count())
        .where(and_(*conditions))
        .group_by(PluginReview.rating)
    )
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for star, count in dist_result.all():
        distribution[star] = count

    return Response.ok(
        data=ReviewSummary(
            avg_rating=round(float(avg_rating), 2),
            rating_count=rating_count,
            rating_distribution=distribution,
        )
    )


@router.post(
    "/plugins/{plugin_id}/reviews",
    response_model=Response[ReviewResponse],
    summary="发表评价",
)
async def create_review(
    plugin_id: uuid.UUID,
    req: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[ReviewResponse]:
    """
    已购用户发表评价。

    校验逻辑：
    1. 插件存在且已发布
    2. 用户已购买该插件
    3. 用户尚未评价该插件（含软删除的记录也不允许重复）
    """
    # 校验插件存在
    plugin_result = await db.execute(
        select(Plugin).where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
    )
    plugin = plugin_result.scalar_one_or_none()
    if plugin is None:
        raise NotFoundError("插件不存在")

    # 校验已购
    purchase_result = await db.execute(
        select(UserPurchase).where(
            UserPurchase.user_id == current_user.id,
            UserPurchase.plugin_id == plugin_id,
        )
    )
    purchase = purchase_result.scalar_one_or_none()
    if purchase is None:
        raise BadRequestError("请先购买该插件后再评价")

    # 校验未重复评价
    existing = await db.execute(
        select(PluginReview).where(
            PluginReview.plugin_id == plugin_id,
            PluginReview.user_id == current_user.id,
            PluginReview.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("你已经评价过该插件")

    review = PluginReview(
        id=uuid.uuid4(),
        plugin_id=plugin_id,
        user_id=current_user.id,
        order_id=purchase.order_id,
        rating=req.rating,
        title=req.title,
        content=req.content,
    )
    db.add(review)
    await db.flush()

    # 同步更新插件冗余评分
    await _sync_plugin_rating(plugin_id, db)

    return Response.ok(
        data=ReviewResponse(
            id=review.id,
            plugin_id=review.plugin_id,
            user_id=review.user_id,
            order_id=review.order_id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_visible=review.is_visible,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user_nickname=current_user.nickname,
            user_avatar_url=current_user.avatar_url or "",
        ),
        message="评价发表成功",
    )


@router.delete(
    "/plugins/{plugin_id}/reviews/{review_id}",
    response_model=Response[dict],
    summary="删除评价",
)
async def delete_review(
    plugin_id: uuid.UUID,
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """仅评价作者可软删除自己的评价，同步更新插件冗余评分。"""
    result = await db.execute(
        select(PluginReview).where(
            PluginReview.id == review_id,
            PluginReview.plugin_id == plugin_id,
            PluginReview.deleted_at.is_(None),
        )
    )
    review = result.scalar_one_or_none()
    if review is None:
        raise NotFoundError("评价不存在")

    if review.user_id != current_user.id:
        raise ForbiddenError("只能删除自己的评价")

    review.deleted_at = datetime.now(timezone.utc)
    db.add(review)
    await db.flush()

    # 同步更新插件冗余评分
    await _sync_plugin_rating(plugin_id, db)

    return Response.ok(
        data={"review_id": str(review_id)},
        message="评价已删除",
    )
