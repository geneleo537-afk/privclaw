"""
用户相关 ORM 模型：User、UserProfile。

User 为核心账号表，支持买家/开发者双身份。
UserProfile 为扩展信息表，与 User 一对一关联。
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
from sqlalchemy.dialects.postgresql import INET, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.plugin import Plugin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    用户核心表。

    - role: buyer（纯买家）| developer（已激活开发者）| admin（管理员）
    - status: active | suspended | banned
    - email 字段存储加密后的值（pgcrypto），email_hash 用于唯一约束和登录查询
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="登录邮箱，pgcrypto 对称加密存储",
    )
    email_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        comment="邮箱 SHA-256 哈希，用于唯一性校验和登录查询",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt 哈希密码",
    )
    nickname: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户昵称",
    )
    avatar_url: Mapped[str] = mapped_column(
        String(512),
        server_default="",
        comment="头像 URL",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="buyer",
        comment="角色：buyer / developer / admin",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        comment="账号状态：active / suspended / banned",
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="邮箱是否已验证",
    )
    is_developer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="是否已激活开发者身份",
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True,
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        uselist=False,
        lazy="select",
        cascade="all, delete-orphan",
    )
    plugins: Mapped[list["Plugin"]] = relationship(
        back_populates="developer",
        foreign_keys="Plugin.developer_id",
        lazy="select",
    )


class UserProfile(Base, TimestampMixin):
    """
    用户扩展信息表。

    包含开发者资料（bio、website 等）和财务信息（支付宝账号等）。
    敏感字段在应用层加密后存储，此处仅存储密文字符串。
    """

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="关联的用户 ID",
    )
    real_name: Mapped[str] = mapped_column(
        String(100),
        server_default="",
        comment="真实姓名（AES-256-GCM 加密存储）",
    )
    phone: Mapped[str] = mapped_column(
        String(255),
        server_default="",
        comment="手机号（加密存储）",
    )
    phone_hash: Mapped[str] = mapped_column(
        String(64),
        server_default="",
        comment="手机号哈希，用于查询",
    )
    bio: Mapped[str] = mapped_column(Text, server_default="", comment="个人简介")
    website: Mapped[str] = mapped_column(String(512), server_default="")
    github_url: Mapped[str] = mapped_column(String(512), server_default="")
    company: Mapped[str] = mapped_column(String(200), server_default="")

    # 财务信息（敏感字段，加密存储）
    bank_account: Mapped[str] = mapped_column(String(255), server_default="")
    bank_name: Mapped[str] = mapped_column(String(100), server_default="")
    alipay_account: Mapped[str] = mapped_column(String(255), server_default="")
    wechat_pay_account: Mapped[str] = mapped_column(String(255), server_default="")

    # 开发者统计冗余字段（定期从源表同步）
    total_plugins: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_sales: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00"
    )
    avg_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, server_default="0.00"
    )

    # ─── 关系 ────────────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        back_populates="profile",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_profiles_user_id_orm"),
    )
