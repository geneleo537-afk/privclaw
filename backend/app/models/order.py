"""
订单相关 ORM 模型：Order、UserPurchase。

Order 记录每笔购买交易，包含金额、分账、支付状态和插件快照。
UserPurchase 为用户已购插件速查表，从 Order 派生，支持快速鉴权。
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    """
    订单表。

    status 状态机：pending -> paid -> refunding -> refunded | cancelled | closed
    plugin_snapshot 在下单时固化插件信息，防止插件修改后历史订单数据丢失。
    order_no 格式：LC + 年月日 + 序列号，如 LC2026031100001。
    """

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_no: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        comment="平台订单号，格式 LC + 年月日 + 序列号",
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="买家用户 ID",
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugins.id", ondelete="RESTRICT"),
        nullable=False,
        comment="购买的插件 ID",
    )
    plugin_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plugin_versions.id", ondelete="SET NULL"),
        nullable=True,
        comment="购买时的版本 ID",
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="开发者 ID（冗余，加速分账查询）",
    )

    # 金额信息
    original_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="原价"
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="实付金额"
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00", comment="优惠金额"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="CNY"
    )

    # 分账信息
    platform_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00", comment="平台抽成（30%）"
    )
    developer_revenue: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00", comment="开发者收入（70%）"
    )
    fee_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), nullable=False, server_default="0.3000", comment="平台费率"
    )

    # 支付信息
    payment_method: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="", comment="wechat_pay / alipay"
    )
    payment_channel: Mapped[str] = mapped_column(String(50), server_default="")
    third_party_tx_id: Mapped[str] = mapped_column(
        String(128), server_default="", comment="第三方支付流水号"
    )

    # 状态机
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        comment="pending / paid / refunding / refunded / cancelled / closed",
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="订单过期时间，未支付超时自动关闭",
    )

    # 插件快照（下单时记录，不随插件更新变化）
    plugin_snapshot: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="'{}'::jsonb",
        comment="下单时刻的插件快照（name、version、price 等）",
    )


class UserPurchase(Base):
    """
    用户已购插件速查表。

    从 orders 表派生，在订单支付成功后写入。
    UNIQUE(user_id, plugin_id) 确保同一用户不重复购买同一插件。
    """

    __tablename__ = "user_purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plugin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False
    )
    purchased_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default="NOW()",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "plugin_id", name="uq_user_purchase_orm"),
    )
