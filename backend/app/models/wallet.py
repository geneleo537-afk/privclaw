"""
钱包相关 ORM 模型：Transaction（交易流水）、Settlement（结算）。

注意：任务描述中提到的 wallets/wallet_transactions/withdrawals 三张表
在实际 schema.sql 中对应 transactions（流水）和 settlements（结算）。
为保持与数据库结构一致，使用实际表名建模。

Transaction：只追加不修改，完整记录每笔资金变动。
Settlement：按周期汇总开发者收入，发起提现结算。
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Transaction(Base):
    """
    交易流水表（只追加，不允许修改或删除）。

    type: payment / refund / settlement / withdrawal / platform_fee
    direction: in（入账）| out（出账）
    balance_before / balance_after 记录资金变动前后余额，便于审计。
    """

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tx_no: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        comment="交易流水号，业务层保证唯一",
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=True,
        comment="关联订单 ID（提现等非订单交易为 NULL）",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="关联用户 ID",
    )
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="交易类型：payment / refund / settlement / withdrawal / platform_fee",
    )
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="资金方向：in=入账 / out=出账",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="交易金额（必须为正数）"
    )
    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="交易前可用余额"
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="交易后可用余额"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="CNY"
    )
    payment_method: Mapped[str] = mapped_column(String(20), server_default="")
    third_party_tx_id: Mapped[str] = mapped_column(
        String(128), server_default="", comment="第三方支付流水号"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )
    description: Mapped[str] = mapped_column(Text, server_default="")
    tx_metadata: Mapped[dict] = mapped_column(
        "metadata",  # DB 列名保持 metadata，Python 属性改名避免与 SQLAlchemy 保留字冲突
        JSONB, nullable=False, server_default="'{}'::jsonb"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default="NOW()",
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_transactions_amount_positive"),
        CheckConstraint("direction IN ('in', 'out')", name="chk_transactions_direction_orm"),
    )


class Settlement(Base, TimestampMixin):
    """
    结算表。

    按 7/15 天周期汇总开发者收入，每个周期对同一开发者唯一（联合唯一约束）。
    final_amount 为最终结算金额，不能为负数（CHECK 约束保护）。
    """

    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    settlement_no: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        comment="结算单号，业务层生成",
    )
    developer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="开发者用户 ID",
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False, comment="结算周期起始日")
    period_end: Mapped[date] = mapped_column(Date, nullable=False, comment="结算周期截止日")
    total_order_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="周期内订单总金额"
    )
    platform_fee_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="平台抽成总额"
    )
    developer_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="开发者应得金额"
    )
    adjustment_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0.00",
        comment="调整金额（退款扣减等，可为负）",
    )
    final_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0.00", comment="最终结算金额（不能为负）"
    )
    order_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", comment="涉及订单数"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        comment="pending / processing / completed / failed / cancelled",
    )
    withdrawal_method: Mapped[str] = mapped_column(
        String(20), server_default="", comment="提现方式：bank / alipay / wechat_pay"
    )
    withdrawal_account: Mapped[str] = mapped_column(
        String(255), server_default="", comment="提现账号（加密存储）"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    failure_reason: Mapped[str] = mapped_column(Text, server_default="")

    __table_args__ = (
        # 注意：原 uq_settlement_developer_period 唯一约束已在迁移 002 中删除，
        # Settlement 现用作按需提现申请，同一开发者同月可多次申请。
        CheckConstraint("final_amount >= 0", name="chk_settlements_final_amount_orm"),
    )
