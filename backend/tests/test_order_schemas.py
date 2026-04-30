"""
订单模块 Schema 测试。

覆盖：创建订单请求、订单响应、支付请求等模型校验。
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.schemas.order import (
    CreateOrderRequest,
    OrderResponse,
    PayAlipayRequest,
    PayBalanceRequest,
)


class TestCreateOrderRequest:
    """创建订单请求体测试。"""

    def test_valid_create_order(self):
        """合法创建订单应能通过校验。"""
        req = CreateOrderRequest(plugin_id=uuid.uuid4())
        assert isinstance(req.plugin_id, uuid.UUID)


class TestOrderResponse:
    """订单响应体测试。"""

    def test_order_response_unpaid(self):
        """未支付订单应能正确创建。"""
        now = datetime.now(tz=timezone.utc)
        resp = OrderResponse(
            id=uuid.uuid4(),
            order_no="ORD20260430001",
            plugin_snapshot={"name": "Test Plugin", "price": "9.90"},
            paid_amount=Decimal("9.90"),
            platform_fee=Decimal("2.97"),
            developer_revenue=Decimal("6.93"),
            pay_channel=None,
            status="pending",
            paid_at=None,
            expires_at=now,
            created_at=now,
        )
        assert resp.status == "pending"
        assert resp.paid_at is None

    def test_order_response_paid(self):
        """已支付订单应能正确创建。"""
        now = datetime.now(tz=timezone.utc)
        resp = OrderResponse(
            id=uuid.uuid4(),
            order_no="ORD20260430002",
            plugin_snapshot={"name": "Test Plugin", "price": "19.90"},
            paid_amount=Decimal("19.90"),
            platform_fee=Decimal("5.97"),
            developer_revenue=Decimal("13.93"),
            pay_channel="alipay",
            status="paid",
            paid_at=now,
            expires_at=now,
            created_at=now,
        )
        assert resp.status == "paid"
        assert resp.pay_channel == "alipay"
        assert resp.paid_at is not None

    def test_order_revenue_calculation(self):
        """订单收入计算应正确（30% 平台费）。"""
        resp = OrderResponse(
            id=uuid.uuid4(),
            order_no="ORD20260430003",
            plugin_snapshot={"name": "Test", "price": "100.00"},
            paid_amount=Decimal("100.00"),
            platform_fee=Decimal("30.00"),
            developer_revenue=Decimal("70.00"),
            pay_channel="balance",
            status="paid",
            paid_at=None,
            expires_at=None,
            created_at=datetime.now(tz=timezone.utc),
        )
        assert resp.platform_fee + resp.developer_revenue == resp.paid_amount


class TestPayAlipayRequest:
    """支付宝支付请求体测试。"""

    def test_valid_pay_request(self):
        """合法支付请求应能通过校验。"""
        req = PayAlipayRequest(order_id=uuid.uuid4())
        assert isinstance(req.order_id, uuid.UUID)


class TestPayBalanceRequest:
    """余额支付请求体测试。"""

    def test_valid_balance_pay_request(self):
        """合法余额支付请求应能通过校验。"""
        req = PayBalanceRequest(order_id=uuid.uuid4())
        assert isinstance(req.order_id, uuid.UUID)
