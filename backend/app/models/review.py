"""
插件评价 ORM 模型：PluginReview。

每位用户对同一插件只能留一条评价（UniqueConstraint），
软删除后不影响唯一约束（应用层控制）。
"""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.plugin import Plugin
    from app.models.user import User


class PluginReview(Base, TimestampMixin, SoftDeleteMixin):
    """
    插件评价表。

    rating 范围 1-5（数据库 CHECK 约束在迁移脚本中定义）。
    同一用户同一插件只能有一条未删除评价，由应用层校验 + 唯一约束双重保障。
    """

    __tablename__ = "plugin_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugins.id", ondelete="CASCADE"),
        nullable=False,
        comment="被评价的插件 ID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="评价者用户 ID",
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联订单 ID（可选）",
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="评分 1-5",
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        server_default="",
        comment="评价标题",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="",
        comment="评价内容",
    )
    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="是否可见（管理员可隐藏）",
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        lazy="select",
    )
    plugin: Mapped["Plugin"] = relationship(
        foreign_keys=[plugin_id],
        lazy="select",
    )

    __table_args__ = (
        UniqueConstraint("plugin_id", "user_id", name="uq_plugin_review_user"),
    )
