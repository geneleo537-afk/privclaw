"""
余额支付提供商实现。

直接扣减用户钱包余额，无需跳转第三方支付页面。
- create_payment：检查余额 -> 调用 WalletService.debit 扣减
- verify_callback：余额支付为同步完成，无异步回调，直接返回成功
- refund：调用 WalletService.credit 将金额退回用户余额

注意：此 Provider 依赖数据库 Session 和 user_id，
构造时需传入，不能作为单例使用。
"""
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.payment.base import (
    CallbackResult,
    PaymentProvider,
    PaymentResult,
    RefundResult,
)
from app.services.wallet_service import WalletService


class BalanceProvider(PaymentProvider):
    """余额支付——直接扣减用户钱包余额，同步完成，无二维码。"""

    def __init__(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        self.db = db
        self.user_id = user_id

    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> PaymentResult:
        """
        余额扣减支付。

        先查询余额确认充足，再调用 debit 扣减。
        余额不足返回失败结果，不抛异常，由调用方决定如何处理。
        """
        wallet_svc = WalletService(self.db)
        balance_info = await wallet_svc.get_balance(self.user_id)

        if balance_info["balance"] < amount:
            return PaymentResult(
                success=False,
                order_no=order_no,
                error=f"余额不足，当前余额 {balance_info['balance']}，需支付 {amount}",
            )

        await wallet_svc.debit(
            user_id=self.user_id,
            amount=amount,
            description=f"购买：{subject}（订单 {order_no}）",
            tx_type="payment",
        )
        return PaymentResult(success=True, order_no=order_no)

    def verify_callback(self, data: dict) -> CallbackResult:
        """
        余额支付无异步回调，此方法用于接口统一，直接解析传入的数据。

        调用方在余额扣减成功后可以直接构造 data 调用此方法，
        无需真实的第三方签名验证。
        """
        order_no = data.get("order_no", "")
        amount_str = data.get("amount", "0")
        try:
            paid_amount = Decimal(amount_str)
        except Exception:
            paid_amount = Decimal("0")

        return CallbackResult(
            success=True,
            order_no=order_no,
            trade_no="",  # 余额支付无第三方流水号
            paid_amount=paid_amount,
        )

    async def refund(
        self, order_no: str, amount: Decimal, reason: str
    ) -> RefundResult:
        """
        余额退款：将金额原路退回用户钱包。

        type='refund'，direction='in'，通过 WalletService.credit 实现。
        """
        wallet_svc = WalletService(self.db)
        await wallet_svc.credit(
            user_id=self.user_id,
            order_id=None,
            amount=amount,
            description=f"退款：{reason}（订单 {order_no}）",
        )
        return RefundResult(success=True, refund_no=order_no)
