"""
支付宝支付提供商实现（当面付 - 扫码支付）。

使用 alipay-sdk-python 库（alipay-sdk-python==3.7.x）实现：
- create_payment：调用 alipay.trade.precreate 生成二维码 URL
- verify_callback：验证支付宝异步通知签名
- refund：调用 alipay.trade.refund 发起退款

注意：
- AliPay 实例在构造时初始化一次，不在请求内重复创建
- sandbox 环境通过 settings.APP_ENV == "development" 自动切换
- 签名类型固定使用 RSA2（推荐），不支持 RSA1
"""
import logging
from decimal import Decimal

from alipay import AliPay
from alipay.utils import AliPayConfig

from app.core.config import settings
from app.services.payment.base import (
    CallbackResult,
    PaymentProvider,
    PaymentResult,
    RefundResult,
)

logger = logging.getLogger(__name__)


class AlipayProvider(PaymentProvider):
    """支付宝当面付实现（扫码 -> 用户支付 -> 异步回调）。"""

    def __init__(self) -> None:
        self.client = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL,
            app_private_key_string=settings.ALIPAY_PRIVATE_KEY,
            alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
            sign_type="RSA2",
            debug=(settings.APP_ENV == "development"),
            config=AliPayConfig(timeout=15),
        )

    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> PaymentResult:
        """
        调用支付宝当面付预创建接口，返回二维码 URL。

        接口文档：alipay.trade.precreate
        成功时 response["code"] == "10000"，qr_code 字段包含二维码内容（URL 格式）。
        """
        try:
            response = self.client.api_alipay_trade_precreate(
                out_trade_no=order_no,
                total_amount=str(amount),
                subject=subject,
            )
        except Exception as e:
            logger.exception("支付宝 precreate 接口调用异常，order_no=%s", order_no)
            return PaymentResult(success=False, error=f"支付接口异常：{e}")

        # 支付宝 SDK 返回字典，code "10000" 表示成功
        if response.get("code") != "10000":
            sub_msg = response.get("sub_msg") or response.get("msg", "未知错误")
            logger.warning(
                "支付宝 precreate 失败，order_no=%s，msg=%s", order_no, sub_msg
            )
            return PaymentResult(success=False, order_no=order_no, error=sub_msg)

        qr_code_url = response.get("qr_code", "")
        return PaymentResult(success=True, qr_code_url=qr_code_url, order_no=order_no)

    def verify_callback(self, data: dict) -> CallbackResult:
        """
        验证支付宝异步通知签名，解析回调结果。

        支付宝 SDK verify() 方法：
        - 提取并移除 sign、sign_type 字段
        - 用支付宝公钥验证剩余参数的 RSA2 签名
        - 返回 True/False

        trade_status == "TRADE_SUCCESS" 表示交易成功。
        """
        # 深拷贝，避免修改原始 data（verify 会 pop sign）
        params = dict(data)
        sign = params.pop("sign", None)
        params.pop("sign_type", None)

        if not sign:
            return CallbackResult(success=False, error="回调缺少 sign 字段")

        try:
            verified = self.client.verify(params, sign)
        except Exception as e:
            logger.exception("支付宝回调签名验证异常")
            return CallbackResult(success=False, error=f"签名验证异常：{e}")

        if not verified:
            return CallbackResult(success=False, error="签名验证失败")

        trade_status = data.get("trade_status", "")
        if trade_status != "TRADE_SUCCESS":
            return CallbackResult(
                success=False,
                error=f"交易状态非成功：{trade_status}",
            )

        order_no = data.get("out_trade_no", "")
        trade_no = data.get("trade_no", "")
        paid_amount = Decimal(data.get("total_amount", "0"))

        return CallbackResult(
            success=True,
            order_no=order_no,
            trade_no=trade_no,
            paid_amount=paid_amount,
        )

    async def refund(
        self, order_no: str, amount: Decimal, reason: str
    ) -> RefundResult:
        """
        调用支付宝退款接口（alipay.trade.refund）。

        refund_amount 精度到分，reason 展示给支付宝侧（不展示给用户）。
        成功标志：response["code"] == "10000" 且 fund_change == "Y"。
        """
        try:
            response = self.client.api_alipay_trade_refund(
                out_trade_no=order_no,
                refund_amount=str(amount),
                refund_reason=reason,
            )
        except Exception as e:
            logger.exception("支付宝退款接口异常，order_no=%s", order_no)
            return RefundResult(success=False, error=f"退款接口异常：{e}")

        if response.get("code") != "10000":
            sub_msg = response.get("sub_msg") or response.get("msg", "退款失败")
            logger.warning(
                "支付宝退款失败，order_no=%s，msg=%s", order_no, sub_msg
            )
            return RefundResult(success=False, error=sub_msg)

        # fund_change == "Y" 表示资金真实退款（部分场景可能为 N）
        if response.get("fund_change") != "Y":
            logger.warning(
                "支付宝退款 fund_change 非 Y，order_no=%s，response=%s",
                order_no,
                response,
            )

        refund_no = response.get("out_trade_no", order_no)
        return RefundResult(success=True, refund_no=refund_no)
