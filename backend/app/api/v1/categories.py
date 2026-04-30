"""
分类与标签端点：分类列表、热门标签。

GET /categories      — 所有启用的分类列表（树形结构，按 sort_order 排序）
GET /tags/popular    — 热门标签列表（按使用量倒序，取前 20 条）
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.category import PluginCategory, PluginTag
from app.schemas.common import Response

router = APIRouter()


@router.get(
    "/categories",
    response_model=Response[list],
    summary="分类列表",
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> Response[list]:
    """
    返回所有启用状态（is_active=True）的插件分类，按 sort_order 升序排列。

    返回扁平列表，前端根据 parent_id 自行组织树形结构。
    每条记录包含：id、name、slug、icon、parent_id、plugin_count、sort_order。
    """
    result = await db.execute(
        select(PluginCategory)
        .where(PluginCategory.is_active.is_(True))
        .order_by(PluginCategory.sort_order)
    )
    categories = result.scalars().all()

    items = [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "icon": c.icon,
            "description": c.description,
            "parent_id": str(c.parent_id) if c.parent_id else None,
            "plugin_count": c.plugin_count,
            "sort_order": c.sort_order,
        }
        for c in categories
    ]
    return Response.ok(data=items)


@router.get(
    "/tags/popular",
    response_model=Response[list],
    summary="热门标签",
)
async def popular_tags(
    db: AsyncSession = Depends(get_db),
) -> Response[list]:
    """
    返回使用量最多的前 20 个标签，按 plugin_count 降序排列。

    plugin_count 由数据库触发器或定时任务维护，此处直接读取冗余字段。
    """
    result = await db.execute(
        select(PluginTag)
        .order_by(PluginTag.plugin_count.desc())
        .limit(20)
    )
    tags = result.scalars().all()

    items = [
        {
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "plugin_count": t.plugin_count,
        }
        for t in tags
    ]
    return Response.ok(data=items)
