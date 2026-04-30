"""
钱包模块 Schema 测试。

覆盖：提现申请校验、钱包响应模型等。
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.schemas.wallet import (
    WalletResponse,
    TransactionResponse,
    WithdrawRequest,
    WithdrawalResponse,
)


class TestWalletResponse:
    """钱包响应测试。"""

    def test_wallet_response_creation(self):
        """钱包响应应能正确创建。"""
        resp = WalletResponse(
            balance=Decimal("100.50"),
            total_earned=Decimal("500.00"),
            total_withdrawn=Decimal("399.50"),
        )
        assert resp.balance == Decimal("100.50")
        assert resp.total_earned == Decimal("500.00")
        assert resp.total_withdrawn == Decimal("399.50")


class TestTransactionResponse:
    """交易流水响应测试。"""

    def test_transaction_response_creation(self):
        """交易流水响应应能正确创建。"""
        now = datetime.now(tz=timezone.utc)
        resp = TransactionResponse(
            id=uuid.uuid4(),
            type="purchase",
            direction="out",
            amount=Decimal("9.90"),
            balance_after=Decimal("90.10"),
            description="购买插件",
            created_at=now,
        )
        assert resp.type == "purchase"
        assert resp.direction == "out"
        assert resp.amount == Decimal("9.90")


class TestWithdrawRequest:
    """提现申请请求体测试。"""

    def test_valid_withdraw_request(self):
        """合法提现申请应能通过校验。"""
        req = WithdrawRequest(
            amount=Decimal("100.00"),
            alipay_account="user@example.com",
            alipay_name="张三",
        )
        assert req.amount == Decimal("100.00")

    def test_withdraw_zero_amount_fails(self):
        """金额为 0 应校验失败。"""
        with pytest.raises(Exception):
            WithdrawRequest(
                amount=Decimal("0"),
                alipay_account="user@example.com",
                alipay_name="张三",
            )

    def test_withdraw_negative_amount_fails(self):
        """负数金额应校验失败。"""
        with pytest.raises(Exception):
            WithdrawRequest(
                amount=Decimal("-50.00"),
                alipay_account="user@example.com",
                alipay_name="张三",
            )

    def test_withdraw_empty_account_fails(self):
        """空支付宝账号应校验失败。"""
        with pytest.raises(Exception):
            WithdrawRequest(
                amount=Decimal("100.00"),
                alipay_account="",
                alipay_name="张三",
            )


class TestWithdrawalResponse:
    """提现记录响应测试。"""

    def test_withdrawal_response_pending(self):
        """待审核提现记录应能正确创建。"""
        now = datetime.now(tz=timezone.utc)
        resp = WithdrawalResponse(
            id=uuid.uuid4(),
            amount=Decimal("200.00"),
            alipay_account="dev@example.com",
            status="pending",
            requested_at=now,
            completed_at=None,
            admin_note=None,
        )
        assert resp.status == "pending"
        assert resp.completed_at is None

    def test_withdrawal_response_completed(self):
        """已完成提现记录应能正确创建。"""
        now = datetime.now(tz=timezone.utc)
        resp = WithdrawalResponse(
            id=uuid.uuid4(),
            amount=Decimal("200.00"),
            alipay_account="dev@example.com",
            status="completed",
            requested_at=now,
            completed_at=now,
            admin_note="已打款",
        )
        assert resp.status == "completed"
        assert resp.admin_note == "已打款"
