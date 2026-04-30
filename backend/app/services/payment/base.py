"""
支付提供商抽象基类与数据契约定义。

所有支付渠道（支付宝、余额等）必须实现此接口，调用方通过多态统一调用，
不依赖具体渠道实现，便于后续接入微信支付等其他渠道。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PaymentResult:
    """发起支付的结果。"""

    success: bool
    # 支付二维码 URL（当面付/扫码支付场景）
    qr_code_url: str = ""
    # 商户订单号（透传，便于调用方追踪）
    order_no: str = ""
    error: str = ""


@dataclass
class CallbackResult:
    """支付渠道异步回调的解析结果。"""

    success: bool
    # 商户订单号（对应 Order.order_no）
    order_no: str = ""
    # 第三方流水号（对应 Order.third_party_tx_id）
    trade_no: str = ""
    paid_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    error: str = ""


@dataclass
class RefundResult:
    """退款结果。"""

    success: bool
    refund_no: str = ""
    error: str = ""


class PaymentProvider(ABC):
    """
    支付提供商抽象基类。

    所有渠道实现必须继承此类并实现全部抽象方法。
    异步方法统一使用 async/await，同步方法（verify_callback）
    因支付宝 SDK 的签名验证为同步 I/O 而设计为同步。
    """

    @abstractmethod
    async def create_payment(
        self, order_no: str, amount: Decimal, subject: str
    ) -> PaymentResult:
        """
        发起支付请求。

        Args:
            order_no: 商户订单号（全局唯一）
            amount:   实付金额（Decimal，精度到分）
            subject:  订单标题（展示给用户）

        Returns:
            PaymentResult，成功时 qr_code_url 非空（扫码支付场景）
        """

    @abstractmethod
    def verify_callback(self, data: dict) -> CallbackResult:
        """
        验证支付渠道异步通知的签名并解析结果。

        设计为同步方法：支付宝 SDK verify 为同步操作，无 I/O 阻塞。

        Args:
            data: 回调请求的原始参数字典（POST form-data 解析后）

        Returns:
            CallbackResult，success=False 时 error 字段说明原因
        """

    @abstractmethod
    async def refund(
        self, order_no: str, amount: Decimal, reason: str
    ) -> RefundResult:
        """
        发起退款请求。

        Args:
            order_no: 原商户订单号
            amount:   退款金额（不超过原付金额）
            reason:   退款原因（展示给渠道方）

        Returns:
            RefundResult
        """
