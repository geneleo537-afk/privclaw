"""
插件服务：插件 CRUD、版本管理、发布流程。

设计要点：
- slug 自动生成：名称转 kebab-case + 数字后缀保证唯一
- 状态流转：draft -> published（发布）/ suspended（软删除）
- 分页统一返回 {"items", "total", "page", "page_size"} 格式
- 版本号严格遵循 semver X.Y.Z 格式
"""
import re
import uuid
from typing import Optional

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.category import PluginTag
from app.models.plugin import Plugin, PluginTagRelation, PluginVersion
from app.schemas.plugin import CreatePluginRequest, UpdatePluginRequest

# semver 正则：匹配 X.Y.Z，X/Y/Z 均为非负整数，无前导零
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# 合法排序字段白名单，防止 SQL 注入
_SORT_FIELDS = {
    "created_at": Plugin.created_at,
    "download_count": Plugin.download_count,
    "avg_rating": Plugin.avg_rating,
    "price": Plugin.price,
}


def _to_kebab_case(name: str) -> str:
    """
    将插件名称转换为 kebab-case slug 基础部分。

    处理规则：
    - 转小写
    - 非字母数字字符替换为连字符
    - 合并连续连字符
    - 去除首尾连字符
    """
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    # 限制基础 slug 最大长度，为后缀预留空间
    return slug[:150] if slug else "plugin"


async def _generate_unique_slug(db: AsyncSession, name: str) -> str:
    """
    生成全局唯一的 slug。

    策略：先尝试 base-slug，若已存在则追加 -2, -3, ... 直至找到空位。
    最多尝试 999 次，防止极端情况下的无限循环。
    """
    base = _to_kebab_case(name)
    candidate = base
    for suffix in range(2, 1001):
        existing = await db.scalar(select(Plugin).where(Plugin.slug == candidate))
        if existing is None:
            return candidate
        candidate = f"{base}-{suffix}"
    raise BadRequestError("无法生成唯一 slug，请更换插件名称")


class PluginService:
    """插件业务逻辑服务。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_plugins(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        tag: Optional[str] = None,
        sort_by: str = "created_at",
        status: str = "published",
    ) -> dict:
        """
        插件列表查询（前台展示）。

        - 仅返回未软删除的插件（deleted_at IS NULL）
        - search 对 name/summary/description 进行 ILIKE 模糊搜索
        - tag 参数按标签名称过滤
        - sort_by 只接受白名单字段，默认降序排列
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        query = select(Plugin).where(
            Plugin.status == status,
            Plugin.deleted_at.is_(None),
        )

        # 全文搜索（ILIKE，兼容无 GIN 索引的开发环境）
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Plugin.name.ilike(pattern),
                    Plugin.summary.ilike(pattern),
                    Plugin.description.ilike(pattern),
                )
            )

        # 分类过滤
        if category_id is not None:
            query = query.where(Plugin.category_id == category_id)

        # 标签过滤：通过关联表 JOIN
        if tag is not None:
            query = (
                query
                .join(PluginTagRelation, PluginTagRelation.plugin_id == Plugin.id)
                .join(PluginTag, PluginTag.id == PluginTagRelation.tag_id)
                .where(PluginTag.name == tag)
            )

        # 排序：仅允许白名单字段，防止注入
        sort_col = _SORT_FIELDS.get(sort_by, Plugin.created_at)
        query = query.order_by(desc(sort_col))

        # 总数查询（复用过滤条件）
        count_query = select(func.count()).select_from(query.subquery())
        total: int = await self.db.scalar(count_query) or 0

        # 分页
        items_query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(items_query)
        items = result.scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_plugin(self, plugin_id: uuid.UUID) -> Plugin:
        """查找插件，不存在或已软删除则抛 NotFoundError。"""
        plugin = await self.db.scalar(
            select(Plugin).where(
                Plugin.id == plugin_id,
                Plugin.deleted_at.is_(None),
            )
        )
        if plugin is None:
            raise NotFoundError("插件不存在")
        return plugin

    async def get_plugin_by_slug(self, slug: str) -> Plugin:
        """通过 slug 查找插件，不存在则抛 NotFoundError。"""
        plugin = await self.db.scalar(
            select(Plugin).where(
                Plugin.slug == slug,
                Plugin.deleted_at.is_(None),
            )
        )
        if plugin is None:
            raise NotFoundError(f"插件 '{slug}' 不存在")
        return plugin

    async def create_plugin(
        self, developer_id: uuid.UUID, req: CreatePluginRequest
    ) -> Plugin:
        """
        创建插件草稿。

        - 自动生成全局唯一 slug（kebab-case + 数字后缀）
        - 价格为 0 时自动标记 is_free=True
        - 初始状态为 draft，需手动调用 publish_plugin 发布
        - 如有 tag_ids，创建对应的关联记录
        """
        slug = await _generate_unique_slug(self.db, req.name)

        plugin = Plugin(
            id=uuid.uuid4(),
            developer_id=developer_id,
            name=req.name,
            slug=slug,
            summary=req.summary,
            description=req.description,
            icon_url=req.icon_url,
            price=req.price,
            is_free=(req.price == 0),
            category_id=req.category_id,
            status="draft",
            review_status="pending",
        )
        self.db.add(plugin)
        await self.db.flush()  # 获取 plugin.id，用于插入关联记录

        # 处理标签关联
        for tag_id in req.tag_ids:
            relation = PluginTagRelation(plugin_id=plugin.id, tag_id=tag_id)
            self.db.add(relation)

        await self.db.commit()
        await self.db.refresh(plugin)
        return plugin

    async def update_plugin(
        self,
        plugin_id: uuid.UUID,
        developer_id: uuid.UUID,
        data: dict,
    ) -> Plugin:
        """
        更新插件信息。

        - 检查插件归属（developer_id 必须一致）
        - 只更新 data 中存在的字段（partial update）
        - 若 price 被更新，同步更新 is_free 标志
        - 若 tag_ids 存在，重建标签关联
        """
        plugin = await self.get_plugin(plugin_id)
        if plugin.developer_id != developer_id:
            raise ForbiddenError("无权修改此插件")

        # 允许更新的字段集合
        allowed_fields = {
            "name", "summary", "description", "icon_url",
            "price", "category_id", "screenshots",
        }

        for field, value in data.items():
            if field in allowed_fields and value is not None:
                setattr(plugin, field, value)

        # price 变更时同步 is_free
        if "price" in data and data["price"] is not None:
            plugin.is_free = data["price"] == 0

        # 重建标签关联
        if "tag_ids" in data and data["tag_ids"] is not None:
            await self.db.execute(
                PluginTagRelation.__table__.delete().where(
                    PluginTagRelation.plugin_id == plugin_id
                )
            )
            for tag_id in data["tag_ids"]:
                self.db.add(PluginTagRelation(plugin_id=plugin_id, tag_id=tag_id))

        await self.db.commit()
        await self.db.refresh(plugin)
        return plugin

    async def publish_plugin(
        self, plugin_id: uuid.UUID, developer_id: uuid.UUID
    ) -> Plugin:
        """
        发布插件（draft -> published）。

        前置条件：
        - 插件必须处于 draft 或 suspended 状态
        - 调用者必须是插件开发者
        """
        plugin = await self.get_plugin(plugin_id)
        if plugin.developer_id != developer_id:
            raise ForbiddenError("无权发布此插件")

        if plugin.status not in ("draft", "suspended"):
            raise BadRequestError(f"当前状态 '{plugin.status}' 不允许发布")

        plugin.status = "published"

        from datetime import datetime, timezone
        if plugin.published_at is None:
            plugin.published_at = datetime.now(tz=timezone.utc)

        await self.db.commit()
        await self.db.refresh(plugin)
        return plugin

    async def delete_plugin(
        self, plugin_id: uuid.UUID, developer_id: uuid.UUID
    ) -> None:
        """
        软删除插件（status -> suspended，deleted_at 记录时间）。

        不物理删除，保留历史订单关联数据。
        """
        plugin = await self.get_plugin(plugin_id)
        if plugin.developer_id != developer_id:
            raise ForbiddenError("无权删除此插件")

        from datetime import datetime, timezone
        plugin.status = "suspended"
        plugin.deleted_at = datetime.now(tz=timezone.utc)

        await self.db.commit()

    async def add_version(
        self,
        plugin_id: uuid.UUID,
        developer_id: uuid.UUID,
        version: str,
        file_key: str,
        file_size: int,
        sha256: str,
        changelog: str,
    ) -> PluginVersion:
        """
        为插件添加新版本。

        约束：
        - version 必须符合 semver X.Y.Z 格式
        - 同一插件下版本号唯一
        - 创建成功后更新 plugin.current_version 和 plugin.current_version_id
        """
        # semver 格式校验
        if not _SEMVER_RE.match(version):
            raise BadRequestError(f"版本号 '{version}' 格式不符合 semver（X.Y.Z）规范")

        plugin = await self.get_plugin(plugin_id)
        if plugin.developer_id != developer_id:
            raise ForbiddenError("无权为此插件添加版本")

        # 版本号唯一性检查
        existing_version = await self.db.scalar(
            select(PluginVersion).where(
                and_(
                    PluginVersion.plugin_id == plugin_id,
                    PluginVersion.version == version,
                )
            )
        )
        if existing_version is not None:
            raise BadRequestError(f"版本 '{version}' 已存在")

        plugin_version = PluginVersion(
            id=uuid.uuid4(),
            plugin_id=plugin_id,
            version=version,
            file_url=file_key,
            file_hash_sha256=sha256,
            file_size_bytes=file_size,
            changelog=changelog,
            status="pending",
        )
        self.db.add(plugin_version)
        await self.db.flush()

        # 更新插件当前版本冗余字段
        plugin.current_version = version
        plugin.current_version_id = plugin_version.id

        await self.db.commit()
        await self.db.refresh(plugin_version)
        return plugin_version

    async def get_developer_plugins(
        self,
        developer_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        查询开发者的所有插件（包含所有状态，不过滤软删除）。

        开发者后台需要看到所有插件（含 draft / suspended），故不过滤 deleted_at。
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        base_query = select(Plugin).where(Plugin.developer_id == developer_id)

        total: int = await self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        ) or 0

        result = await self.db.execute(
            base_query
            .order_by(desc(Plugin.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }
