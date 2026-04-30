"""
插件相关 ORM 模型：Plugin、PluginTagRelation、PluginVersion。

Plugin 为插件主表，PluginVersion 管理版本历史，
PluginTagRelation 为插件-标签多对多关联表。
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import PluginCategory, PluginTag
    from app.models.user import User


class PluginTagRelation(Base):
    """
    插件与标签多对多关联表（复合主键）。

    使用 SQLAlchemy 显式关联对象模式，以便未来扩展关联属性。
    """

    __tablename__ = "plugin_tag_relations"

    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugins.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default="NOW()",
        nullable=False,
    )


class Plugin(Base, TimestampMixin, SoftDeleteMixin):
    """
    插件主表。

    status 状态机：draft -> pending_review -> published | suspended | removed
    current_version_id 为当前最新已发布版本的 ID，加速列表页查询。
    search_vector 由数据库触发器自动维护，覆盖 name + summary + description 全文搜索。
    """

    __tablename__ = "plugins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="开发者用户 ID",
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="所属分类 ID",
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        comment="URL 友好标识，自动添加 clawstore- 前缀",
    )
    summary: Mapped[str] = mapped_column(
        String(500), nullable=False, server_default="", comment="一句话简介"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="", comment="详细描述（Markdown）"
    )
    icon_url: Mapped[str] = mapped_column(String(512), server_default="")
    screenshots: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="'[]'::jsonb",
        comment="截图 URL 数组",
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="CNY"
    )
    is_free: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="draft",
        comment="draft / pending_review / published / suspended / removed",
    )
    review_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )
    review_note: Mapped[str] = mapped_column(Text, server_default="")

    # 统计冗余字段（由触发器或定时任务维护，读多写少）
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    purchase_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    avg_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, server_default="0.00"
    )
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    # 当前版本快照（冗余，加速列表页）
    current_version: Mapped[str] = mapped_column(String(50), server_default="")
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_versions.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        comment="当前最新版本 ID（use_alter 解决循环外键）",
    )

    # 全文搜索向量（数据库触发器自动维护）
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

    published_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    developer: Mapped["User"] = relationship(
        back_populates="plugins",
        foreign_keys=[developer_id],
        lazy="select",
    )
    category: Mapped[Optional["PluginCategory"]] = relationship(
        back_populates="plugins",
        foreign_keys=[category_id],
        lazy="select",
    )
    versions: Mapped[list["PluginVersion"]] = relationship(
        back_populates="plugin",
        foreign_keys="PluginVersion.plugin_id",
        lazy="select",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["PluginTag"]] = relationship(
        secondary="plugin_tag_relations",
        back_populates="plugins",
        lazy="select",
    )


class PluginVersion(Base):
    """
    插件版本管理表。

    每次发布新版本创建一条记录，版本号在同一 plugin_id 下唯一。
    status 状态：pending -> approved | rejected | yanked
    """

    __tablename__ = "plugin_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugins.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属插件 ID",
    )
    version: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="语义化版本号，如 1.0.0"
    )
    changelog: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="", comment="变更日志（Markdown）"
    )
    file_url: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="插件包对象存储地址"
    )
    file_hash_sha256: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="文件 SHA-256 校验值"
    )
    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger, nullable=False, server_default="0"
    )
    min_claw_version: Mapped[str] = mapped_column(String(50), server_default="")
    max_claw_version: Mapped[str] = mapped_column(String(50), server_default="")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        comment="pending / approved / rejected / yanked",
    )
    review_note: Mapped[str] = mapped_column(Text, server_default="")
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    published_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default="NOW()",
        nullable=False,
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    plugin: Mapped["Plugin"] = relationship(
        back_populates="versions",
        foreign_keys=[plugin_id],
    )

    __table_args__ = (
        UniqueConstraint("plugin_id", "version", name="uq_plugin_version_orm"),
    )
