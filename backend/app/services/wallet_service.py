"""
钱包服务：基于 transactions 表的余额管理与提现申请。

设计要点：
- 无独立 wallets 表，余额 = SUM(in) - SUM(out) 从 transactions 聚合
- balance_before / balance_after 在每次写入时快照，方便审计和对账
- debit 操作先加锁检查余额，防止并发超扣（依赖数据库事务）
- tx_no 流水号格式：TX + 时间戳毫秒 + 6位随机字符
- 提现申请通过 settlements 表管理，状态由后台运营处理
"""
import random
import string
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.models.wallet import Settlement, Transaction


def _gen_tx_no() -> str:
    """生成唯一流水号：TX + 毫秒时间戳 + 6位大写字母数字。"""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S%f")[:17]
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TX{ts}{suffix}"


def _gen_settlement_no() -> str:
    """生成结算单号：SL + 毫秒时间戳 + 6位大写字母数字。"""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S%f")[:17]
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SL{ts}{suffix}"


class WalletService:
    """基于 transactions 表的余额服务。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_balance(self, user_id: uuid.UUID) -> dict:
        """
        计算用户可用余额。

        算法：
        - total_in  = SUM(amount WHERE user_id=X AND direction='in'  AND status='completed')
        - total_out = SUM(amount WHERE user_id=X AND direction='out' AND status='completed')
        - balance   = total_in - total_out

        返回：{"balance": Decimal, "total_earned": Decimal, "total_withdrawn": Decimal}
        """
        in_sum: Decimal = await self.db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0.00")))
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.direction == "in",
                    Transaction.status == "completed",
                )
            )
        ) or Decimal("0.00")

        out_sum: Decimal = await self.db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0.00")))
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.direction == "out",
                    Transaction.status == "completed",
                )
            )
        ) or Decimal("0.00")

        return {
            "balance": in_sum - out_sum,
            "total_earned": in_sum,
            "total_withdrawn": out_sum,
        }

    async def credit(
        self,
        user_id: uuid.UUID,
        order_id: Optional[uuid.UUID],
        amount: Decimal,
        description: str,
    ) -> Transaction:
        """
        开发者收入入账（direction='in'，type='settlement'）。

        在支付回调成功后由 OrderService.mark_paid 调用。
        balance_after = 当前余额 + amount。
        """
        if amount <= 0:
            raise BadRequestError("入账金额必须为正数")

        balance_info = await self.get_balance(user_id)
        balance_before = balance_info["balance"]
        balance_after = balance_before + amount

        tx = Transaction(
            id=uuid.uuid4(),
            tx_no=_gen_tx_no(),
            order_id=order_id,
            user_id=user_id,
            type="settlement",
            direction="in",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status="completed",
            description=description,
        )
        self.db.add(tx)
        await self.db.flush()
        return tx

    async def debit(
        self,
        user_id: uuid.UUID,
        amount: Decimal,
        description: str,
        order_id: Optional[uuid.UUID] = None,
        tx_type: str = "payment",
    ) -> Transaction:
        """
        余额扣减（direction='out'）。

        调用方通过 tx_type 区分业务类型：
        - "payment"    ：用户余额购买插件
        - "withdrawal" ：提现申请扣减

        先检查余额充足再写入，防止超扣。
        依赖外部事务保证原子性（调用方需在同一事务内 commit）。
        """
        if amount <= 0:
            raise BadRequestError("扣减金额必须为正数")

        balance_info = await self.get_balance(user_id)
        balance_before = balance_info["balance"]

        if balance_before < amount:
            raise BadRequestError(
                f"余额不足，当前余额 {balance_before}，需扣减 {amount}"
            )

        balance_after = balance_before - amount

        tx = Transaction(
            id=uuid.uuid4(),
            tx_no=_gen_tx_no(),
            order_id=order_id,
            user_id=user_id,
            type=tx_type,
            direction="out",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status="completed",
            description=description,
        )
        self.db.add(tx)
        await self.db.flush()
        return tx

    async def get_transactions(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        查询用户流水列表（按创建时间降序）。

        返回：{"items": [...], "total": N, "page": page, "page_size": page_size}
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        base_query = select(Transaction).where(Transaction.user_id == user_id)

        total: int = await self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        ) or 0

        result = await self.db.execute(
            base_query
            .order_by(desc(Transaction.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def request_withdrawal(
        self,
        user_id: uuid.UUID,
        amount: Decimal,
        alipay_account: str,
        alipay_name: str,
    ) -> Settlement:
        """
        申请提现。

        流程：
        1. 校验金额 >= WITHDRAW_MIN_AMOUNT
        2. 检查余额充足
        3. 扣减余额（type='withdrawal'）
        4. 创建 Settlement 记录（status='pending'，等待运营审核打款）
        """
        min_amount = Decimal(str(settings.WITHDRAW_MIN_AMOUNT))
        if amount < min_amount:
            raise BadRequestError(f"最低提现金额为 {min_amount} 元")

        # debit 内部已检查余额充足，余额不足时抛 BadRequestError
        await self.debit(
            user_id=user_id,
            amount=amount,
            description=f"提现申请：支付宝 {alipay_account}",
            tx_type="withdrawal",
        )

        from datetime import date
        today = date.today()
        settlement = Settlement(
            id=uuid.uuid4(),
            settlement_no=_gen_settlement_no(),
            developer_id=user_id,
            period_start=today,
            period_end=today,
            total_order_amount=Decimal("0.00"),
            platform_fee_total=Decimal("0.00"),
            developer_amount=amount,
            adjustment_amount=Decimal("0.00"),
            final_amount=amount,
            order_count=0,
            status="pending",
            withdrawal_method="alipay",
            # alipay_account 为敏感信息，调用方应在传入前完成加密
            withdrawal_account=alipay_account,
        )
        self.db.add(settlement)
        await self.db.commit()
        await self.db.refresh(settlement)
        return settlement

    async def get_withdrawals(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        查询用户提现记录（按创建时间降序）。

        返回：{"items": [...], "total": N, "page": page, "page_size": page_size}
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        base_query = select(Settlement).where(Settlement.developer_id == user_id)

        total: int = await self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        ) or 0

        result = await self.db.execute(
            base_query
            .order_by(desc(Settlement.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
        }
