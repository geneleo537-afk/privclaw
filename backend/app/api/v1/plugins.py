"""
插件端点：列表查询、详情、创建、更新、删除、版本管理、下载。

GET    /plugins                      — 公开插件列表（分页+搜索+分类过滤）
GET    /plugins/{plugin_id}          — 插件详情（公开）
POST   /plugins                      — 创建插件（仅开发者）
PUT    /plugins/{plugin_id}          — 更新插件（仅本人开发者）
DELETE /plugins/{plugin_id}          — 软删除插件（仅本人开发者）
POST   /plugins/{plugin_id}/versions — 上传新版本（仅本人开发者）
GET    /plugins/{plugin_id}/versions — 版本历史列表
GET    /plugins/{plugin_id}/download — 下载插件（需已购买或插件免费）
"""
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response as RawResponse
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, get_optional_user, require_developer
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.category import PluginCategory, PluginTag
from app.models.order import UserPurchase
from app.models.plugin import Plugin, PluginTagRelation, PluginVersion
from app.models.user import User
from app.schemas.common import PageData, PageResponse, Response
from app.schemas.plugin import (
    CreatePluginRequest,
    PluginListItem,
    PluginResponse,
    UpdatePluginRequest,
)
from app.services.storage import get_storage_backend

router = APIRouter()


def _build_plugin_response(plugin: Plugin) -> PluginResponse:
    """将 Plugin ORM 对象转换为 PluginResponse，提取标签名称列表。"""
    tag_names = [tag.name for tag in (plugin.tags or [])]
    return PluginResponse(
        id=plugin.id,
        name=plugin.name,
        slug=plugin.slug,
        summary=plugin.summary,
        description=plugin.description,
        icon_url=plugin.icon_url,
        screenshots=plugin.screenshots if plugin.screenshots else [],
        price=plugin.price,
        currency=plugin.currency,
        is_free=plugin.is_free,
        status=plugin.status,
        review_status=plugin.review_status,
        current_version=plugin.current_version,
        current_version_id=plugin.current_version_id,
        download_count=plugin.download_count,
        purchase_count=plugin.purchase_count,
        avg_rating=plugin.avg_rating,
        rating_count=plugin.rating_count,
        developer_id=plugin.developer_id,
        developer_nickname=plugin.developer.nickname if plugin.developer else "",
        category_id=plugin.category_id,
        category_name=plugin.category.name if plugin.category else None,
        category_slug=plugin.category.slug if plugin.category else None,
        tags=tag_names,
        published_at=plugin.published_at,
        created_at=plugin.created_at,
        updated_at=plugin.updated_at,
    )


def _parse_plugin_identifier(identifier: str) -> tuple[bool, object]:
    """尝试将插件标识解析为 UUID；失败时按 slug 处理。"""
    try:
        return True, uuid.UUID(identifier)
    except ValueError:
        return False, identifier


@router.get(
    "/plugins",
    response_model=PageResponse[PluginListItem],
    summary="公开插件列表",
)
async def list_plugins(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    search: Optional[str] = Query(None, description="关键词搜索（名称/简介）"),
    category_id: Optional[uuid.UUID] = Query(None, description="分类 ID 过滤"),
    category: Optional[str] = Query(None, description="分类 slug 过滤"),
    sort_by: str = Query(
        "created_at",
        description="排序字段：created_at / download_count / avg_rating / price_asc / price_desc",
    ),
    db: AsyncSession = Depends(get_db),
) -> PageResponse[PluginListItem]:
    """
    查询已发布的公开插件列表，支持关键词搜索、分类过滤和排序。

    - 仅返回 status='published' 且未被软删除的插件
    - search 参数对 name 和 summary 进行 ILIKE 模糊匹配
    - sort_by 支持：created_at（最新）、download_count（最热）、avg_rating（最佳评分）
    """
    offset = (page - 1) * page_size

    # 构建过滤条件
    conditions = [
        Plugin.status == "published",
        Plugin.deleted_at.is_(None),
    ]
    if search:
        keyword = f"%{search}%"
        conditions.append(
            or_(
                Plugin.name.ilike(keyword),
                Plugin.summary.ilike(keyword),
                Plugin.description.ilike(keyword),
            )
        )
    if category_id:
        conditions.append(Plugin.category_id == category_id)
    if category:
        conditions.append(PluginCategory.slug == category)

    # 确定排序列
    sort_column_map = {
        "created_at": Plugin.created_at.desc(),
        "download_count": Plugin.download_count.desc(),
        "avg_rating": Plugin.avg_rating.desc(),
        "price_asc": Plugin.price.asc(),
        "price_desc": Plugin.price.desc(),
    }
    order_clause = sort_column_map.get(sort_by, Plugin.created_at.desc())

    # 统计总数
    count_result = await db.execute(
        select(func.count())
        .select_from(Plugin)
        .outerjoin(PluginCategory, Plugin.category_id == PluginCategory.id)
        .where(and_(*conditions))
    )
    total: int = count_result.scalar_one()

    # 分页查询
    plugin_result = await db.execute(
        select(Plugin)
        .outerjoin(PluginCategory, Plugin.category_id == PluginCategory.id)
        .where(and_(*conditions))
        .options(
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
        .order_by(order_clause)
        .offset(offset)
        .limit(page_size)
    )
    plugins = plugin_result.scalars().all()

    items = [
        PluginListItem(
            id=p.id,
            name=p.name,
            slug=p.slug,
            summary=p.summary,
            icon_url=p.icon_url,
            price=p.price,
            is_free=p.is_free,
            status=p.status,
            current_version=p.current_version,
            download_count=p.download_count,
            avg_rating=p.avg_rating,
            rating_count=p.rating_count,
            developer_id=p.developer_id,
            developer_nickname=p.developer.nickname if p.developer else "",
            category_name=p.category.name if p.category else None,
            category_slug=p.category.slug if p.category else None,
        )
        for p in plugins
    ]
    page_data = PageData(items=items, total=total, page=page, page_size=page_size)
    return PageResponse.ok(data=page_data)


@router.get(
    "/plugins/{plugin_identifier}",
    response_model=Response[PluginResponse],
    summary="插件详情",
)
async def get_plugin(
    plugin_identifier: str,
    db: AsyncSession = Depends(get_db),
) -> Response[PluginResponse]:
    """
    获取插件详情，含完整描述、截图、标签列表。
    已发布的插件对所有人公开；草稿/待审核状态仅允许开发者本人查看（通过其他端点实现）。
    """
    is_uuid, identifier_value = _parse_plugin_identifier(plugin_identifier)
    if is_uuid:
        lookup = Plugin.id == identifier_value
    else:
        lookup = Plugin.slug == identifier_value

    result = await db.execute(
        select(Plugin)
        .where(lookup, Plugin.deleted_at.is_(None))
        .options(
            selectinload(Plugin.tags),
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()

    if plugin is None:
        raise NotFoundError("插件不存在")

    return Response.ok(data=_build_plugin_response(plugin))


@router.post(
    "/plugins",
    response_model=Response[PluginResponse],
    status_code=201,
    summary="创建插件",
)
async def create_plugin(
    req: CreatePluginRequest,
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[PluginResponse]:
    """
    开发者创建新插件，初始状态为 draft。

    - slug 基于插件名自动生成，添加 clawstore- 前缀并替换特殊字符
    - 若 price > 0 则自动将 is_free 设为 False
    - tag_ids 存在时关联标签（PluginTagRelation）
    """
    # 生成 slug：clawstore-{name_normalized}
    raw_slug = req.name.lower().replace(" ", "-").replace("_", "-")
    # 移除非字母数字和连字符的字符
    import re
    raw_slug = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]", "", raw_slug)
    slug = f"clawstore-{raw_slug}-{uuid.uuid4().hex[:6]}"

    plugin = Plugin(
        id=uuid.uuid4(),
        developer_id=current_user.id,
        category_id=req.category_id,
        name=req.name,
        slug=slug,
        summary=req.summary,
        description=req.description,
        icon_url=req.icon_url,
        price=req.price,
        is_free=req.price == 0,
        status="draft",
        review_status="pending",
    )
    db.add(plugin)
    await db.flush()  # 获取 plugin.id

    # 关联标签
    for tag_id in req.tag_ids:
        relation = PluginTagRelation(
            plugin_id=plugin.id,
            tag_id=tag_id,
        )
        db.add(relation)

    created_result = await db.execute(
        select(Plugin)
        .where(Plugin.id == plugin.id)
        .options(
            selectinload(Plugin.tags),
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
    )
    created_plugin = created_result.scalar_one()

    return Response.ok(data=_build_plugin_response(created_plugin), message="插件创建成功")


@router.put(
    "/plugins/{plugin_id}",
    response_model=Response[PluginResponse],
    summary="更新插件",
)
async def update_plugin(
    plugin_id: uuid.UUID,
    req: UpdatePluginRequest,
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[PluginResponse]:
    """
    更新插件信息，仅限插件所有者操作。

    - 管理员角色可以绕过所有权检查（通过 admin 接口操作状态）
    - 使用 UpdatePluginRequest 中提供的字段进行部分更新
    - 修改 price 时自动同步 is_free 标志
    """
    result = await db.execute(
        select(Plugin)
        .where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
        .options(
            selectinload(Plugin.tags),
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()

    if plugin is None:
        raise NotFoundError("插件不存在")

    # 非管理员只能操作自己的插件
    if current_user.role != "admin" and plugin.developer_id != current_user.id:
        raise ForbiddenError("无权限修改此插件")

    # 部分更新
    if req.name is not None:
        plugin.name = req.name
    if req.summary is not None:
        plugin.summary = req.summary
    if req.description is not None:
        plugin.description = req.description
    if req.icon_url is not None:
        plugin.icon_url = req.icon_url
    if req.price is not None:
        plugin.price = req.price
        plugin.is_free = req.price == 0
    if req.category_id is not None:
        plugin.category_id = req.category_id

    # 更新标签关联
    if req.tag_ids is not None:
        # 删除旧关联
        old_relations = await db.execute(
            select(PluginTagRelation).where(PluginTagRelation.plugin_id == plugin.id)
        )
        for relation in old_relations.scalars().all():
            await db.delete(relation)
        # 写入新关联
        for tag_id in req.tag_ids:
            db.add(PluginTagRelation(plugin_id=plugin.id, tag_id=tag_id))

    db.add(plugin)
    await db.flush()
    updated_result = await db.execute(
        select(Plugin)
        .where(Plugin.id == plugin.id)
        .options(
            selectinload(Plugin.tags),
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
    )
    updated_plugin = updated_result.scalar_one()

    return Response.ok(data=_build_plugin_response(updated_plugin), message="插件更新成功")


@router.delete(
    "/plugins/{plugin_id}",
    response_model=Response[None],
    summary="删除插件（软删除）",
)
async def delete_plugin(
    plugin_id: uuid.UUID,
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[None]:
    """
    软删除插件（设置 deleted_at 时间戳），仅限插件所有者操作。

    已删除的插件不再出现在公开列表中，但历史订单的 plugin_snapshot 数据仍保留。
    """
    result = await db.execute(
        select(Plugin)
        .where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
        .options(
            selectinload(Plugin.tags),
            selectinload(Plugin.developer),
            selectinload(Plugin.category),
        )
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()

    if plugin is None:
        raise NotFoundError("插件不存在")

    if current_user.role != "admin" and plugin.developer_id != current_user.id:
        raise ForbiddenError("无权限删除此插件")

    plugin.deleted_at = datetime.now(timezone.utc)
    plugin.status = "removed"
    db.add(plugin)

    return Response.ok(message="插件已删除")


@router.post(
    "/plugins/{plugin_id}/versions",
    response_model=Response[dict],
    status_code=201,
    summary="上传插件新版本",
)
async def upload_version(
    plugin_id: uuid.UUID,
    version: str = Query(..., description="语义化版本号，如 1.0.0"),
    changelog: Optional[str] = Query(None, description="变更日志（Markdown）"),
    file: UploadFile = File(..., description="插件 zip 包"),
    current_user: User = Depends(require_developer),
    db: AsyncSession = Depends(get_db),
) -> Response[dict]:
    """
    上传插件新版本文件，执行以下步骤：
    1. 验证插件所有权
    2. 检查版本号在同插件下唯一
    3. 读取文件内容并计算 SHA-256 校验值
    4. 创建 PluginVersion 记录（file_url 待存储服务实现后填充）

    注意：当前版本存储服务（MinIO/OSS）尚未实现，file_url 暂存为占位符。
    实际部署时需接入 app.services.storage 模块完成对象上传。
    """
    result = await db.execute(
        select(Plugin).where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()

    if plugin is None:
        raise NotFoundError("插件不存在")

    if current_user.role != "admin" and plugin.developer_id != current_user.id:
        raise ForbiddenError("无权限为此插件上传版本")

    # 检查版本号唯一性
    existing_version = await db.execute(
        select(PluginVersion).where(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.version == version,
        )
    )
    if existing_version.scalar_one_or_none():
        raise BadRequestError(f"版本 {version} 已存在，请使用新版本号")

    # 读取文件内容，计算 SHA-256
    file_content = await file.read()
    file_size = len(file_content)
    file_hash = hashlib.sha256(file_content).hexdigest()

    if file_size == 0:
        raise BadRequestError("上传文件不能为空")

    # 构建对象存储路径并上传
    object_key = f"plugins/{plugin_id}/{version}/{file.filename}"
    storage = get_storage_backend()
    stored_key = await storage.upload(
        key=object_key,
        data=file_content,
        content_type=file.content_type or "application/octet-stream",
    )

    plugin_version = PluginVersion(
        id=uuid.uuid4(),
        plugin_id=plugin_id,
        version=version,
        changelog=changelog or "",
        file_url=stored_key,
        file_hash_sha256=file_hash,
        file_size_bytes=file_size,
        status="pending",
    )
    db.add(plugin_version)
    await db.flush()

    return Response.ok(
        data={
            "version_id": str(plugin_version.id),
            "plugin_id": str(plugin_id),
            "version": version,
            "file_hash_sha256": file_hash,
            "file_size_bytes": file_size,
            "status": "pending",
        },
        message="版本上传成功，待审核",
    )


@router.get(
    "/plugins/{plugin_id}/versions",
    response_model=Response[list],
    summary="插件版本历史列表",
)
async def list_versions(
    plugin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response[list]:
    """
    查询插件所有历史版本，按创建时间倒序排列。
    公开返回已审核（approved）的版本；待审核和被驳回版本不对外展示。
    """
    result = await db.execute(
        select(Plugin).where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()
    if plugin is None:
        raise NotFoundError("插件不存在")

    version_result = await db.execute(
        select(PluginVersion)
        .where(
            PluginVersion.plugin_id == plugin_id,
            PluginVersion.status == "approved",
        )
        .order_by(PluginVersion.created_at.desc())
    )
    versions = version_result.scalars().all()

    items = [
        {
            "id": str(v.id),
            "version": v.version,
            "changelog": v.changelog,
            "file_size_bytes": v.file_size_bytes,
            "download_count": v.download_count,
            "published_at": v.published_at.isoformat() if v.published_at else None,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]
    return Response.ok(data=items)


@router.get(
    "/plugins/{plugin_id}/download",
    summary="下载插件文件",
)
async def download_plugin(
    plugin_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> RawResponse:
    """
    验证下载权限后直接返回文件流（走 HTTPS，无需暴露 MinIO 端口）。

    下载条件（满足其一即可）：
    1. 插件为免费（is_free=True）
    2. 用户在 user_purchases 表中有对应记录
    """
    result = await db.execute(
        select(Plugin).where(Plugin.id == plugin_id, Plugin.deleted_at.is_(None))
    )
    plugin: Optional[Plugin] = result.scalar_one_or_none()
    if plugin is None:
        raise NotFoundError("插件不存在")

    if plugin.status != "published":
        raise BadRequestError("插件尚未发布，无法下载")

    # 付费插件需验证购买记录
    if not plugin.is_free:
        if current_user is None:
            raise ForbiddenError("请先登录后再下载已购插件")
        purchase_result = await db.execute(
            select(UserPurchase).where(
                UserPurchase.user_id == current_user.id,
                UserPurchase.plugin_id == plugin_id,
            )
        )
        if purchase_result.scalar_one_or_none() is None:
            raise ForbiddenError("您尚未购买此插件")

    # 查询当前已批准版本
    if not plugin.current_version_id:
        raise BadRequestError("插件暂无可下载版本")

    version_result = await db.execute(
        select(PluginVersion).where(
            PluginVersion.id == plugin.current_version_id,
            PluginVersion.status == "approved",
        )
    )
    plugin_version: Optional[PluginVersion] = version_result.scalar_one_or_none()
    if plugin_version is None:
        raise BadRequestError("插件暂无可下载版本")

    # 更新下载计数
    plugin.download_count += 1
    plugin_version.download_count += 1
    db.add(plugin)
    db.add(plugin_version)

    # 从存储后端获取文件并直接返回
    storage = get_storage_backend()
    file_data, content_type = await storage.get_object(plugin_version.file_url)

    # 从 file_url 中提取文件名
    filename = plugin_version.file_url.rsplit("/", 1)[-1] if "/" in plugin_version.file_url else f"{plugin.slug}.zip"

    return RawResponse(
        content=file_data,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(file_data)),
        },
    )
