"""
钱包相关 Schema：余额查询、交易流水、提现申请、提现记录。

对应数据库中的 transactions 表（流水）和 settlements 表（结算/提现）。
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    """开发者钱包概览响应体。"""

    balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal


class TransactionResponse(BaseModel):
    """交易流水单条记录响应体。"""

    id: uuid.UUID
    type: str
    direction: str
    amount: Decimal
    balance_after: Decimal
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WithdrawRequest(BaseModel):
    """提现申请请求体。"""

    amount: Decimal = Field(gt=0, description="提现金额，必须大于 0")
    alipay_account: str = Field(min_length=1, max_length=255, description="支付宝账号")
    alipay_name: str = Field(min_length=1, max_length=100, description="支付宝实名")


class WithdrawalResponse(BaseModel):
    """提现记录单条响应体（映射自 Settlement 模型）。"""

    id: uuid.UUID
    amount: Decimal
    alipay_account: str
    status: str
    requested_at: datetime
    completed_at: Optional[datetime]
    admin_note: Optional[str]

    model_config = {"from_attributes": True}
