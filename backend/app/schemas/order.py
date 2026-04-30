"""
订单相关 Schema：创建请求、订单响应、支付请求。

金额字段全部使用 Decimal 保证精度，避免浮点数舍入误差。
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    """创建订单请求体。"""

    plugin_id: uuid.UUID


class OrderResponse(BaseModel):
    """订单详情响应体。"""

    id: uuid.UUID
    order_no: str
    plugin_snapshot: dict
    paid_amount: Decimal
    platform_fee: Decimal
    developer_revenue: Decimal
    pay_channel: Optional[str]
    status: str
    paid_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PayAlipayRequest(BaseModel):
    """发起支付宝支付请求体。"""

    order_id: uuid.UUID


class PayBalanceRequest(BaseModel):
    """发起余额支付请求体。"""

    order_id: uuid.UUID
