"""
订单服务：创建订单、支付回调、余额支付、超时关闭。

设计要点：
- 订单号格式：LC + YYYYMMDD + 6位随机大写字母数字（如 LC202603110A3F2B）
- PLATFORM_FEE_RATE = 30%，计算精度到分（ROUND_HALF_UP）
- mark_paid 幂等处理：已 paid 状态直接返回
- 免费插件下单后直接标记 paid，无需走支付流程
- plugin_snapshot 在下单时快照，防止插件修改影响历史记录
- 超时关闭（pending -> closed）由 Celery 定时任务触发
"""
import random
import string
import uuid
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.order import Order, UserPurchase
from app.models.plugin import Plugin

PLATFORM_FEE_RATE = Decimal("0.30")
# 订单未支付过期时长（分钟）
ORDER_EXPIRE_MINUTES = 30


def calculate_split(paid_amount: Decimal) -> tuple[Decimal, Decimal]:
    """
    计算分账金额。

    返回 (developer_revenue, platform_fee)，保证两者之和精确等于 paid_amount。
    平台抽成向下取整到分，开发者拿剩余部分，避免多扣。
    """
    platform_fee = (paid_amount * PLATFORM_FEE_RATE).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    developer_revenue = paid_amount - platform_fee
    return developer_revenue, platform_fee


def _gen_order_no() -> str:
    """生成订单号：LC + YYYYMMDD + 8位大写字母数字。"""
    date_part = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"LC{date_part}{suffix}"


def _build_plugin_snapshot(plugin: Plugin) -> dict:
    """将插件关键信息快照为 JSONB，防止插件修改后历史订单数据丢失。"""
    return {
        "id": str(plugin.id),
        "name": plugin.name,
        "slug": plugin.slug,
        "summary": plugin.summary,
        "price": str(plugin.price),
        "currency": plugin.currency,
        "current_version": plugin.current_version,
        "developer_id": str(plugin.developer_id),
        "icon_url": plugin.icon_url,
    }


class OrderService:
    """订单业务逻辑服务。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_order(
        self, buyer_id: uuid.UUID, plugin_id: uuid.UUID
    ) -> Order:
        """
        创建订单。

        流程：
        1. 检查插件存在且 status='published'
        2. 检查是否已购买（user_purchases 表）
        3. 免费插件：直接创建 paid 状态订单 + user_purchases 记录
        4. 付费插件：创建 pending 订单，expires_at = now + 30min
        5. 快照插件信息到 plugin_snapshot
        """
        # 查找插件
        plugin = await self.db.scalar(
            select(Plugin).where(
                Plugin.id == plugin_id,
                Plugin.deleted_at.is_(None),
            )
        )
        if plugin is None:
            raise NotFoundError("插件不存在")
        if plugin.status != "published":
            raise BadRequestError("该插件当前不可购买")

        # 重复购买检查
        already_purchased = await self.db.scalar(
            select(UserPurchase).where(
                and_(
                    UserPurchase.user_id == buyer_id,
                    UserPurchase.plugin_id == plugin_id,
                )
            )
        )
        if already_purchased is not None:
            raise BadRequestError("您已购买过该插件")

        developer_revenue, platform_fee = calculate_split(plugin.price)
        now = datetime.now(tz=timezone.utc)
        order_id = uuid.uuid4()
        order_no = _gen_order_no()

        if plugin.is_free:
            # 免费插件直接完成，不设过期时间
            order = Order(
                id=order_id,
                order_no=order_no,
                buyer_id=buyer_id,
                plugin_id=plugin_id,
                developer_id=plugin.developer_id,
                original_price=Decimal("0.00"),
                paid_amount=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
                platform_fee=Decimal("0.00"),
                developer_revenue=Decimal("0.00"),
                fee_rate=PLATFORM_FEE_RATE,
                status="paid",
                paid_at=now,
                plugin_snapshot=_build_plugin_snapshot(plugin),
            )
            self.db.add(order)
            await self.db.flush()

            purchase = UserPurchase(
                id=uuid.uuid4(),
                user_id=buyer_id,
                plugin_id=plugin_id,
                order_id=order_id,
                purchased_at=now,
            )
            self.db.add(purchase)

            # 免费插件下载计数 +1
            plugin.download_count += 1

            await self.db.commit()
            await self.db.refresh(order)
            return order

        # 付费插件：pending 状态，等待支付
        order = Order(
            id=order_id,
            order_no=order_no,
            buyer_id=buyer_id,
            plugin_id=plugin_id,
            plugin_version_id=plugin.current_version_id,
            developer_id=plugin.developer_id,
            original_price=plugin.price,
            paid_amount=plugin.price,
            discount_amount=Decimal("0.00"),
            platform_fee=platform_fee,
            developer_revenue=developer_revenue,
            fee_rate=PLATFORM_FEE_RATE,
            status="pending",
            expires_at=now + timedelta(minutes=ORDER_EXPIRE_MINUTES),
            plugin_snapshot=_build_plugin_snapshot(plugin),
        )
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_order(
        self, order_id: uuid.UUID, user_id: uuid.UUID
    ) -> Order:
        """查询订单，不存在或不属于该用户则抛错。"""
        order = await self.db.scalar(
            select(Order).where(Order.id == order_id)
        )
        if order is None:
            raise NotFoundError("订单不存在")
        if order.buyer_id != user_id:
            raise ForbiddenError("无权查看此订单")
        return order

    async def cancel_order(
        self, order_id: uuid.UUID, user_id: uuid.UUID
    ) -> Order:
        """
        取消订单（只有 pending 状态可取消）。

        已支付订单需走退款流程，不能直接取消。
        """
        order = await self.get_order(order_id, user_id)
        if order.status != "pending":
            raise BadRequestError(f"当前状态 '{order.status}' 不可取消，只有待支付订单可取消")

        order.status = "cancelled"
        order.cancelled_at = datetime.now(tz=timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def mark_paid(
        self,
        order_id: uuid.UUID,
        channel_trade_no: str,
        pay_channel: str,
    ) -> Order:
        """
        支付回调成功后标记订单为已支付（幂等处理）。

        流程：
        1. SELECT FOR UPDATE 锁定订单行，防止并发重入
        2. 已 paid → 直接返回（幂等保证）
        3. 非 pending → 抛错（状态异常）
        4. 更新 status/paid_at/channel_trade_no
        5. 创建 user_purchases 记录
        6. 插件 download_count +1
        7. 开发者余额入账（credit）

        注意：WITH_FOR_UPDATE 在 asyncpg 下通过 with_for_update() 实现。
        """
        # SELECT FOR UPDATE：锁定行防止并发
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .with_for_update()
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundError("订单不存在")

        # 幂等：已 paid 直接返回
        if order.status == "paid":
            return order

        if order.status != "pending":
            raise BadRequestError(
                f"订单状态异常（{order.status}），无法标记为已支付"
            )

        now = datetime.now(tz=timezone.utc)
        order.status = "paid"
        order.paid_at = now
        order.third_party_tx_id = channel_trade_no
        order.payment_channel = pay_channel

        # 创建已购记录
        purchase = UserPurchase(
            id=uuid.uuid4(),
            user_id=order.buyer_id,
            plugin_id=order.plugin_id,
            order_id=order.id,
            purchased_at=now,
        )
        self.db.add(purchase)

        # 更新插件下载计数
        plugin = await self.db.scalar(
            select(Plugin).where(Plugin.id == order.plugin_id)
        )
        if plugin is not None:
            plugin.download_count += 1

        # 开发者余额入账
        from app.services.wallet_service import WalletService
        wallet_svc = WalletService(self.db)
        await wallet_svc.credit(
            user_id=order.developer_id,
            order_id=order.id,
            amount=order.developer_revenue,
            description=f"插件销售收入：{order.plugin_snapshot.get('name', '')} 订单 {order.order_no}",
        )

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def pay_with_balance(
        self, order_id: uuid.UUID, user_id: uuid.UUID
    ) -> Order:
        """
        余额支付。

        流程：
        1. 验证订单归属
        2. 检查订单状态（pending）及过期时间
        3. 扣减余额（WalletService.debit）
        4. 调用 mark_paid 完成后续处理
        """
        order = await self.get_order(order_id, user_id)
        if order.status != "pending":
            raise BadRequestError(f"当前状态 '{order.status}' 不可支付")

        now = datetime.now(tz=timezone.utc)
        if order.expires_at is not None and order.expires_at < now:
            # 过期自动关闭
            order.status = "closed"
            await self.db.commit()
            raise BadRequestError("订单已过期，请重新下单")

        from app.services.wallet_service import WalletService
        wallet_svc = WalletService(self.db)
        await wallet_svc.debit(
            user_id=user_id,
            amount=order.paid_amount,
            description=f"购买插件：{order.plugin_snapshot.get('name', '')} 订单 {order.order_no}",
            order_id=order.id,
            tx_type="payment",
        )

        return await self.mark_paid(
            order_id=order_id,
            channel_trade_no="",
            pay_channel="balance",
        )

    async def get_user_orders(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        查询用户订单列表（按创建时间降序）。

        返回：{"items": [...], "total": N, "page": page, "page_size": page_size}
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        base_query = select(Order).where(Order.buyer_id == user_id)

        total: int = await self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        ) or 0

        result = await self.db.execute(
            base_query
            .order_by(desc(Order.created_at))
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

    async def close_expired_order(self, order_id: uuid.UUID) -> None:
        """
        关闭超时未支付订单（pending -> closed）。

        由 Celery beat 定时任务调用，幂等处理：非 pending 状态直接跳过。
        """
        order = await self.db.scalar(
            select(Order)
            .where(Order.id == order_id)
            .with_for_update(skip_locked=True)
        )
        if order is None:
            return

        # 非 pending 状态无需处理（幂等）
        if order.status != "pending":
            return

        order.status = "closed"
        await self.db.commit()
