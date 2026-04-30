"""
龙虾超市数据库 ORM 模型定义
基于 SQLAlchemy 2.0 声明式映射
"""
from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String, Text, Boolean, Integer, SmallInteger, BigInteger,
    Numeric, Date, Index, CheckConstraint, UniqueConstraint,
    ForeignKey, text, func,
)
from sqlalchemy.dialects.postgresql import (
    UUID, INET, JSONB, TSVECTOR, TIMESTAMP,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
)


class Base(DeclarativeBase):
    """声明式基类"""
    pass


class TimestampMixin:
    """created_at / updated_at 通用混入"""
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """软删除混入"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
    )


# ============================================================================
# 1. 用户表
# ============================================================================
class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户核心表，单账号支持买家和开发者双身份"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="登录邮箱，pgcrypto 对称加密存储",
    )
    email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="邮箱 SHA-256 哈希",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="bcrypt/argon2id 哈希密码",
    )
    nickname: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="昵称",
    )
    avatar_url: Mapped[str] = mapped_column(
        String(512), server_default="", comment="头像 URL",
    )
    role: Mapped[str] = mapped_column(
        String(20), server_default="buyer", nullable=False,
        comment="角色：buyer / developer",
    )
    status: Mapped[str] = mapped_column(
        String(20), server_default="active", nullable=False,
        comment="状态：active / suspended / banned",
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False,
    )
    is_developer: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True,
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        INET, nullable=True,
    )

    # 关系
    profile: Mapped[Optional[UserProfile]] = relationship(
        back_populates="user", uselist=False, lazy="joined",
    )
    plugins: Mapped[list[Plugin]] = relationship(
        back_populates="developer", foreign_keys="Plugin.developer_id",
    )

    __table_args__ = (
        Index("idx_users_email_hash", "email_hash", postgresql_where=text("deleted_at IS NULL")),
        Index("idx_users_status", "status", postgresql_where=text("deleted_at IS NULL")),
        Index("idx_users_created_at", created_at.desc(), postgresql_where=text("deleted_at IS NULL")),
    )


# ============================================================================
# 2. 用户扩展信息表
# ============================================================================
class UserProfile(Base, TimestampMixin):
    """用户扩展信息，包含开发者资料和财务信息"""
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    real_name: Mapped[str] = mapped_column(
        String(100), server_default="", comment="真实姓名（AES-256-GCM 加密）",
    )
    phone: Mapped[str] = mapped_column(
        String(255), server_default="", comment="手机号（加密存储）",
    )
    phone_hash: Mapped[str] = mapped_column(
        String(64), server_default="", comment="手机号哈希",
    )
    bio: Mapped[str] = mapped_column(Text, server_default="")
    website: Mapped[str] = mapped_column(String(512), server_default="")
    github_url: Mapped[str] = mapped_column(String(512), server_default="")
    company: Mapped[str] = mapped_column(String(200), server_default="")

    # 财务信息（加密存储）
    bank_account: Mapped[str] = mapped_column(String(255), server_default="")
    bank_name: Mapped[str] = mapped_column(String(100), server_default="")
    alipay_account: Mapped[str] = mapped_column(String(255), server_default="")
    wechat_pay_account: Mapped[str] = mapped_column(String(255), server_default="")

    # 开发者统计冗余
    total_plugins: Mapped[int] = mapped_column(Integer, server_default="0")
    total_sales: Mapped[int] = mapped_column(Integer, server_default="0")
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    avg_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default="0.00")

    # 关系
    user: Mapped[User] = relationship(back_populates="profile")


# ============================================================================
# 3. 插件分类表
# ============================================================================
class PluginCategory(Base, TimestampMixin):
    """插件分类表，支持树形多级分类"""
    __tablename__ = "plugin_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(String(255), server_default="")
    description: Mapped[str] = mapped_column(Text, server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")
    plugin_count: Mapped[int] = mapped_column(Integer, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    # 自引用关系
    children: Mapped[list[PluginCategory]] = relationship(back_populates="parent")
    parent: Mapped[Optional[PluginCategory]] = relationship(
        back_populates="children", remote_side=[id],
    )
    plugins: Mapped[list[Plugin]] = relationship(back_populates="category")


# ============================================================================
# 4. 标签表
# ============================================================================
class PluginTag(Base):
    """插件标签表"""
    __tablename__ = "plugin_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    plugin_count: Mapped[int] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )

    # 多对多关系
    plugins: Mapped[list[Plugin]] = relationship(
        secondary="plugin_tag_relations", back_populates="tags",
    )


# ============================================================================
# 5. 插件-标签关联表
# ============================================================================
class PluginTagRelation(Base):
    """插件与标签多对多关联"""
    __tablename__ = "plugin_tag_relations"

    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugin_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )


# ============================================================================
# 6. 插件表
# ============================================================================
class Plugin(Base, TimestampMixin, SoftDeleteMixin):
    """插件主表"""
    __tablename__ = "plugins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True,
        comment="自动添加 clawstore- 前缀",
    )
    summary: Mapped[str] = mapped_column(String(500), server_default="")
    description: Mapped[str] = mapped_column(Text, server_default="")
    icon_url: Mapped[str] = mapped_column(String(512), server_default="")
    screenshots: Mapped[dict] = mapped_column(JSONB, server_default="'[]'::jsonb")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0.00")
    currency: Mapped[str] = mapped_column(String(3), server_default="CNY")
    is_free: Mapped[bool] = mapped_column(Boolean, server_default="true")
    status: Mapped[str] = mapped_column(
        String(20), server_default="draft",
        comment="draft / pending_review / published / suspended / removed",
    )
    review_status: Mapped[str] = mapped_column(String(20), server_default="pending")
    review_note: Mapped[str] = mapped_column(Text, server_default="")

    # 统计冗余
    download_count: Mapped[int] = mapped_column(Integer, server_default="0")
    purchase_count: Mapped[int] = mapped_column(Integer, server_default="0")
    avg_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default="0.00")
    rating_count: Mapped[int] = mapped_column(Integer, server_default="0")

    # 当前版本快照
    current_version: Mapped[str] = mapped_column(String(50), server_default="")
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_versions.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
    )

    # 全文搜索
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

    published_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True,
    )

    # 关系
    developer: Mapped[User] = relationship(
        back_populates="plugins", foreign_keys=[developer_id],
    )
    category: Mapped[Optional[PluginCategory]] = relationship(
        back_populates="plugins",
    )
    versions: Mapped[list[PluginVersion]] = relationship(
        back_populates="plugin",
        foreign_keys="PluginVersion.plugin_id",
    )
    tags: Mapped[list[PluginTag]] = relationship(
        secondary="plugin_tag_relations", back_populates="plugins",
    )
    reviews: Mapped[list[PluginReview]] = relationship(back_populates="plugin")


# ============================================================================
# 7. 插件版本表
# ============================================================================
class PluginVersion(Base):
    """插件版本管理表"""
    __tablename__ = "plugin_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    changelog: Mapped[str] = mapped_column(Text, server_default="")
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, server_default="0")
    min_claw_version: Mapped[str] = mapped_column(String(50), server_default="")
    max_claw_version: Mapped[str] = mapped_column(String(50), server_default="")
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending",
        comment="pending / approved / rejected / yanked",
    )
    review_note: Mapped[str] = mapped_column(Text, server_default="")
    download_count: Mapped[int] = mapped_column(Integer, server_default="0")
    published_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )

    # 关系
    plugin: Mapped[Plugin] = relationship(
        back_populates="versions", foreign_keys=[plugin_id],
    )

    __table_args__ = (
        UniqueConstraint("plugin_id", "version", name="uq_plugin_version"),
    )


# ============================================================================
# 8. 订单表
# ============================================================================
class Order(Base, TimestampMixin):
    """订单表"""
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    order_no: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True,
        comment="格式：LC + 年月日 + 序列号",
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="RESTRICT"),
    )
    plugin_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
    )

    # 金额
    original_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0.00")
    currency: Mapped[str] = mapped_column(String(3), server_default="CNY")

    # 分账
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0.00")
    developer_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0.00")
    fee_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), server_default="0.3000")

    # 支付
    payment_method: Mapped[str] = mapped_column(String(20), server_default="")
    payment_channel: Mapped[str] = mapped_column(String(50), server_default="")
    third_party_tx_id: Mapped[str] = mapped_column(String(128), server_default="")

    # 状态
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending",
        comment="pending / paid / refunding / refunded / cancelled / closed",
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    refunded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    # 快照
    plugin_snapshot: Mapped[dict] = mapped_column(JSONB, server_default="'{}'::jsonb")

    __table_args__ = (
        UniqueConstraint(
            "buyer_id", "plugin_id",
            name="uq_orders_buyer_plugin_paid",
            postgresql_where=text("status = 'paid'"),
        ),
    )


# ============================================================================
# 9. 交易流水表
# ============================================================================
class Transaction(Base):
    """交易流水表，只追加不修改"""
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tx_no: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
    )
    type: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="payment / refund / settlement / withdrawal / platform_fee",
    )
    direction: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="in / out",
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_before: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    currency: Mapped[str] = mapped_column(String(3), server_default="CNY")
    payment_method: Mapped[str] = mapped_column(String(20), server_default="")
    third_party_tx_id: Mapped[str] = mapped_column(String(128), server_default="")
    status: Mapped[str] = mapped_column(String(20), server_default="pending")
    description: Mapped[str] = mapped_column(Text, server_default="")
    metadata: Mapped[dict] = mapped_column(JSONB, server_default="'{}'::jsonb")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_transactions_amount_positive"),
        CheckConstraint("direction IN ('in', 'out')", name="chk_transactions_direction"),
    )


# ============================================================================
# 10. 结算表
# ============================================================================
class Settlement(Base, TimestampMixin):
    """结算表，按周期汇总开发者收入"""
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    settlement_no: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_order_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    platform_fee_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    developer_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    adjustment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    order_count: Mapped[int] = mapped_column(Integer, server_default="0")

    status: Mapped[str] = mapped_column(String(20), server_default="pending")
    withdrawal_method: Mapped[str] = mapped_column(String(20), server_default="")
    withdrawal_account: Mapped[str] = mapped_column(String(255), server_default="")
    processed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    failure_reason: Mapped[str] = mapped_column(Text, server_default="")

    __table_args__ = (
        UniqueConstraint(
            "developer_id", "period_start", "period_end",
            name="uq_settlement_developer_period",
        ),
        CheckConstraint("final_amount >= 0", name="chk_settlements_final_amount"),
    )


# ============================================================================
# 11. 下载记录表
# ============================================================================
class Download(Base):
    """下载记录表"""
    __tablename__ = "downloads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"),
    )
    plugin_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugin_versions.id", ondelete="CASCADE"),
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"),
    )
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[str] = mapped_column(String(512), server_default="")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )


# ============================================================================
# 12. 管理操作日志表
# ============================================================================
class AdminLog(Base):
    """管理后台操作审计日志，只追加不修改"""
    __tablename__ = "admin_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"),
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    detail: Mapped[dict] = mapped_column(JSONB, server_default="'{}'::jsonb")
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[str] = mapped_column(String(512), server_default="")
    reason: Mapped[str] = mapped_column(Text, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )


# ============================================================================
# 13. 插件评价表
# ============================================================================
class PluginReview(Base, TimestampMixin, SoftDeleteMixin):
    """插件评价表"""
    __tablename__ = "plugin_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"),
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(200), server_default="")
    content: Mapped[str] = mapped_column(Text, server_default="")
    is_visible: Mapped[bool] = mapped_column(Boolean, server_default="true")

    # 关系
    plugin: Mapped[Plugin] = relationship(back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("plugin_id", "user_id", name="uq_plugin_review_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_review_rating"),
    )


# ============================================================================
# 14. 用户购买记录表
# ============================================================================
class UserPurchase(Base):
    """用户已购插件速查表"""
    __tablename__ = "user_purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"),
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"),
    )
    purchased_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "plugin_id", name="uq_user_purchase"),
    )
