"""
分类与标签 ORM 模型：PluginCategory、PluginTag。

PluginCategory 支持树形多级分类（自引用外键）。
PluginTag 为扁平标签结构。
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.plugin import Plugin


class PluginCategory(Base, TimestampMixin):
    """
    插件分类表。

    支持树形多级分类，parent_id=NULL 代表顶级分类。
    plugin_count 为冗余计数，由触发器或定时任务维护。
    """

    __tablename__ = "plugin_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_categories.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        comment="父分类 ID，NULL 表示顶级分类",
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="URL 友好标识，全局唯一，如 ai-tools",
    )
    icon: Mapped[str] = mapped_column(String(255), server_default="")
    description: Mapped[str] = mapped_column(Text, server_default="")
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", comment="排序权重，值越小越靠前"
    )
    plugin_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", comment="分类下插件数（冗余计数）"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    # 自引用：父子分类
    parent: Mapped[Optional["PluginCategory"]] = relationship(
        back_populates="children",
        remote_side="PluginCategory.id",
        foreign_keys=[parent_id],
        lazy="select",
    )
    children: Mapped[list["PluginCategory"]] = relationship(
        back_populates="parent",
        foreign_keys=[parent_id],
        lazy="select",
    )
    plugins: Mapped[list["Plugin"]] = relationship(
        back_populates="category",
        lazy="select",
    )


class PluginTag(Base):
    """
    插件标签表（扁平结构）。

    plugin_count 为使用此标签的插件数，冗余维护。
    """

    __tablename__ = "plugin_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    plugin_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default="NOW()",
        nullable=False,
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    plugins: Mapped[list["Plugin"]] = relationship(
        secondary="plugin_tag_relations",
        back_populates="tags",
        lazy="select",
    )
