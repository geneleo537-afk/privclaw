"""
本地演示数据初始化脚本。

用途：
1. 创建可直接登录的 admin / developer / buyer 演示账号
2. 创建分类、标签、已发布插件与版本文件
3. 为开发者生成一笔已完成订单对应的收益流水
4. 让本地环境在迁移完成后具备“可浏览 / 可下单 / 可下载”的基础数据

推荐执行方式：
    docker compose exec backend python -m app.scripts.seed_demo
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import json
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models.category import PluginCategory, PluginTag
from app.models.order import Order, UserPurchase
from app.models.plugin import Plugin, PluginTagRelation, PluginVersion
from app.models.user import User, UserProfile
from app.models.wallet import Transaction
from app.services.storage import get_storage_backend
from app.utils.clawstore_prefix import ClawstorePrefixProcessor


DEMO_PASSWORD = "Demo123456"
ADMIN_PASSWORD = "Admin123456"
FEE_RATE = Decimal("0.3000")


@dataclass(frozen=True)
class DemoPluginSpec:
    slug: str
    name: str
    summary: str
    description: str
    version: str
    price: Decimal
    category_slug: str
    category_name: str
    tag_slug: str
    tag_name: str
    order_no: str | None = None


PLUGIN_SPECS = [
    DemoPluginSpec(
        slug="clawstore-demo-free-assistant",
        name="Demo 免费助手",
        summary="用于本地验证免费插件详情、下单与下载链路。",
        description="本地演示插件，重点用于验证免费插件的浏览与下载流程。",
        version="1.0.0",
        price=Decimal("0.00"),
        category_slug="productivity",
        category_name="生产力",
        tag_slug="demo",
        tag_name="Demo",
    ),
    DemoPluginSpec(
        slug="clawstore-demo-paid-pro",
        name="Demo 付费专业版",
        summary="一款已售出的付费插件，便于验证订单、已购列表与开发者钱包。",
        description="此插件会为演示买家生成一笔已完成订单，同时为演示开发者生成收益流水。",
        version="1.2.0",
        price=Decimal("39.00"),
        category_slug="devtools",
        category_name="开发工具",
        tag_slug="paid-demo",
        tag_name="付费演示",
        order_no="DMO202603110001",
    ),
    DemoPluginSpec(
        slug="clawstore-demo-paid-starter",
        name="Demo 付费入门版",
        summary="未购买的付费插件，用于本地下单与支付页联调。",
        description="此插件默认不上任何已购记录，适合本地从详情页创建订单后进入 checkout 流程。",
        version="1.0.1",
        price=Decimal("19.00"),
        category_slug="ai",
        category_name="AI 增强",
        tag_slug="local-flow",
        tag_name="本地联调",
    ),
]


def email_hash(email: str) -> str:
    return hashlib.sha256(email.lower().encode()).hexdigest()


def tx_no(suffix: str) -> str:
    return f"TXDEMO{suffix}"


def build_demo_archive(
    *,
    plugin_name: str,
    plugin_id: str,
    version: str,
    description: str,
) -> bytes:
    """构造一个最小可下载的演示插件 ZIP。"""
    manifest = {
        "id": plugin_id,
        "name": plugin_name,
        "version": version,
        "description": description,
    }

    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "manifest.json",
                json.dumps(manifest, ensure_ascii=False, indent=2),
            )
            zf.writestr(
                "README.md",
                f"# {plugin_name}\n\n{description}\n",
            )
            zf.writestr(
                "main.py",
                (
                    '"""本地演示插件入口。"""\n'
                    "def run():\n"
                    f"    return 'hello from {plugin_name} {version}'\n"
                ),
            )

        return buffer.getvalue()


async def get_or_create_user(
    session,
    *,
    email: str,
    nickname: str,
    password: str,
    role: str,
    is_developer: bool,
) -> User:
    result = await session.execute(
        select(User).where(User.email_hash == email_hash(email))
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            email_hash=email_hash(email),
            password_hash=hash_password(password),
            nickname=nickname,
            role=role,
            status="active",
            email_verified=True,
            is_developer=is_developer,
        )
        session.add(user)
        await session.flush()
    else:
        user.nickname = nickname
        user.role = role
        user.status = "active"
        user.email_verified = True
        user.is_developer = is_developer
        session.add(user)

    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(id=uuid.uuid4(), user_id=user.id)
        session.add(profile)

    if role == "developer":
        profile.bio = "本地演示开发者账号，用于验证发布、收益与钱包页面。"
        profile.company = "PrivClaw Demo"
    elif role == "admin":
        profile.bio = "本地演示管理员账号。"
        profile.company = "PrivClaw Ops"
    else:
        profile.bio = "本地演示买家账号。"
        profile.company = "PrivClaw QA"

    return user


async def get_or_create_category(session, *, slug: str, name: str) -> PluginCategory:
    result = await session.execute(
        select(PluginCategory).where(PluginCategory.slug == slug)
    )
    category = result.scalar_one_or_none()
    if category is None:
        category = PluginCategory(
            id=uuid.uuid4(),
            slug=slug,
            name=name,
            icon="🦞",
            description=f"{name} 分类（本地演示）",
            sort_order=0,
            is_active=True,
        )
        session.add(category)
        await session.flush()
    else:
        category.name = name
        category.description = f"{name} 分类（本地演示）"
        category.is_active = True
        session.add(category)
    return category


async def get_or_create_tag(session, *, slug: str, name: str) -> PluginTag:
    result = await session.execute(select(PluginTag).where(PluginTag.slug == slug))
    tag = result.scalar_one_or_none()
    if tag is None:
        tag = PluginTag(
            id=uuid.uuid4(),
            slug=slug,
            name=name,
            plugin_count=0,
        )
        session.add(tag)
        await session.flush()
    else:
        tag.name = name
        session.add(tag)
    return tag


async def get_or_create_plugin(
    session,
    *,
    developer: User,
    category: PluginCategory,
    tag: PluginTag,
    spec: DemoPluginSpec,
    storage,
) -> Plugin:
    result = await session.execute(select(Plugin).where(Plugin.slug == spec.slug))
    plugin = result.scalar_one_or_none()

    if plugin is None:
        plugin = Plugin(
            id=uuid.uuid4(),
            developer_id=developer.id,
            category_id=category.id,
            name=spec.name,
            slug=spec.slug,
            summary=spec.summary,
            description=spec.description,
            icon_url="",
            screenshots=[],
            price=spec.price,
            currency="CNY",
            is_free=spec.price == 0,
            status="published",
            review_status="approved",
            review_note="本地 demo 数据",
            purchase_count=0,
            download_count=0,
            avg_rating=Decimal("4.80"),
            rating_count=12,
            published_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        session.add(plugin)
        await session.flush()
    else:
        plugin.developer_id = developer.id
        plugin.category_id = category.id
        plugin.name = spec.name
        plugin.summary = spec.summary
        plugin.description = spec.description
        plugin.price = spec.price
        plugin.is_free = spec.price == 0
        plugin.status = "published"
        plugin.review_status = "approved"
        plugin.review_note = "本地 demo 数据"
        plugin.published_at = plugin.published_at or (
            datetime.now(timezone.utc) - timedelta(days=1)
        )
        session.add(plugin)

    relation_result = await session.execute(
        select(PluginTagRelation).where(
            PluginTagRelation.plugin_id == plugin.id,
            PluginTagRelation.tag_id == tag.id,
        )
    )
    if relation_result.scalar_one_or_none() is None:
        session.add(
            PluginTagRelation(plugin_id=plugin.id, tag_id=tag.id)
        )

    raw_archive = build_demo_archive(
        plugin_name=spec.name,
        plugin_id=spec.slug.replace("clawstore-", ""),
        version=spec.version,
        description=spec.description,
    )
    processed_archive, report = ClawstorePrefixProcessor().process(raw_archive)
    if not report.success:
        raise RuntimeError(
            f"演示插件包处理失败：{spec.slug}，错误：{report.error or 'unknown'}"
        )

    object_key = f"demo/{spec.slug}/{spec.version}/{spec.slug}.zip"
    stored_key = await storage.upload(
        key=object_key,
        data=processed_archive,
        content_type="application/zip",
    )

    version_result = await session.execute(
        select(PluginVersion).where(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.version == spec.version,
        )
    )
    version = version_result.scalar_one_or_none()
    if version is None:
        version = PluginVersion(
            id=uuid.uuid4(),
            plugin_id=plugin.id,
            version=spec.version,
            changelog="本地 demo 初始化版本",
            file_url=stored_key,
            file_hash_sha256=hashlib.sha256(processed_archive).hexdigest(),
            file_size_bytes=len(processed_archive),
            min_claw_version="0.1.0",
            max_claw_version="",
            status="approved",
            review_note="自动生成的本地 demo 版本",
            download_count=0,
            published_at=datetime.now(timezone.utc) - timedelta(hours=12),
        )
        session.add(version)
        await session.flush()
    else:
        version.changelog = "本地 demo 初始化版本"
        version.file_url = stored_key
        version.file_hash_sha256 = hashlib.sha256(processed_archive).hexdigest()
        version.file_size_bytes = len(processed_archive)
        version.status = "approved"
        version.review_note = "自动生成的本地 demo 版本"
        version.published_at = version.published_at or (
            datetime.now(timezone.utc) - timedelta(hours=12)
        )
        session.add(version)

    plugin.current_version = spec.version
    plugin.current_version_id = version.id
    return plugin


async def ensure_demo_paid_order(
    session,
    *,
    buyer: User,
    developer: User,
    plugin: Plugin,
    order_no: str,
) -> None:
    """创建一笔已完成订单、已购记录和开发者收益流水。"""
    result = await session.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()

    platform_fee = (plugin.price * Decimal("0.30")).quantize(Decimal("0.01"))
    developer_revenue = (plugin.price - platform_fee).quantize(Decimal("0.01"))
    paid_at = datetime.now(timezone.utc) - timedelta(hours=6)

    snapshot = {
        "plugin_id": str(plugin.id),
        "name": plugin.name,
        "version": plugin.current_version,
        "price": str(plugin.price),
        "currency": plugin.currency,
        "icon_url": plugin.icon_url,
        "summary": plugin.summary,
    }

    if order is None:
        order = Order(
            id=uuid.uuid4(),
            order_no=order_no,
            buyer_id=buyer.id,
            plugin_id=plugin.id,
            plugin_version_id=plugin.current_version_id,
            developer_id=developer.id,
            original_price=plugin.price,
            paid_amount=plugin.price,
            discount_amount=Decimal("0.00"),
            currency="CNY",
            platform_fee=platform_fee,
            developer_revenue=developer_revenue,
            fee_rate=FEE_RATE,
            payment_method="alipay",
            payment_channel="alipay",
            third_party_tx_id="ALIPAY-DEMO-0001",
            status="paid",
            paid_at=paid_at,
            plugin_snapshot=snapshot,
        )
        session.add(order)
        await session.flush()
    else:
        order.buyer_id = buyer.id
        order.plugin_id = plugin.id
        order.plugin_version_id = plugin.current_version_id
        order.developer_id = developer.id
        order.original_price = plugin.price
        order.paid_amount = plugin.price
        order.platform_fee = platform_fee
        order.developer_revenue = developer_revenue
        order.fee_rate = FEE_RATE
        order.payment_method = "alipay"
        order.payment_channel = "alipay"
        order.third_party_tx_id = "ALIPAY-DEMO-0001"
        order.status = "paid"
        order.paid_at = paid_at
        order.plugin_snapshot = snapshot
        session.add(order)

    purchase_result = await session.execute(
        select(UserPurchase).where(
            UserPurchase.user_id == buyer.id,
            UserPurchase.plugin_id == plugin.id,
        )
    )
    if purchase_result.scalar_one_or_none() is None:
        session.add(
            UserPurchase(
                id=uuid.uuid4(),
                user_id=buyer.id,
                plugin_id=plugin.id,
                order_id=order.id,
                purchased_at=paid_at,
            )
        )

    tx_result = await session.execute(
        select(Transaction).where(Transaction.tx_no == tx_no("000001"))
    )
    if tx_result.scalar_one_or_none() is None:
        session.add(
            Transaction(
                id=uuid.uuid4(),
                tx_no=tx_no("000001"),
                order_id=order.id,
                user_id=developer.id,
                type="settlement",
                direction="in",
                amount=developer_revenue,
                balance_before=Decimal("0.00"),
                balance_after=developer_revenue,
                payment_method="alipay",
                third_party_tx_id="ALIPAY-DEMO-0001",
                status="completed",
                description=f"Demo 订单收益：{plugin.name}",
            )
        )

    plugin.purchase_count = 1
    plugin.download_count = max(plugin.download_count, 1)
    plugin.avg_rating = Decimal("4.90")
    plugin.rating_count = max(plugin.rating_count, 18)
    session.add(plugin)


async def update_demo_counters(
    session,
    *,
    developer: User,
    categories: list[PluginCategory],
    tags: list[PluginTag],
) -> None:
    category_plugin_counts = {}
    for category in categories:
        result = await session.execute(
            select(Plugin).where(
                Plugin.category_id == category.id,
                Plugin.deleted_at.is_(None),
            )
        )
        category_plugin_counts[category.id] = len(result.scalars().all())

    for category in categories:
        category.plugin_count = category_plugin_counts.get(category.id, 0)
        session.add(category)

    for tag in tags:
        result = await session.execute(
            select(PluginTagRelation).where(PluginTagRelation.tag_id == tag.id)
        )
        tag.plugin_count = len(result.scalars().all())
        session.add(tag)

    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == developer.id)
    )
    profile = profile_result.scalar_one()
    profile.total_plugins = sum(category.plugin_count for category in categories)
    profile.total_sales = 1
    profile.total_revenue = Decimal("27.30")
    profile.avg_rating = Decimal("4.90")
    session.add(profile)


async def seed_demo() -> None:
    async with AsyncSessionLocal() as session:
        storage = get_storage_backend()

        admin = await get_or_create_user(
            session,
            email="admin@demo.privclaw.com",
            nickname="本地管理员",
            password=ADMIN_PASSWORD,
            role="admin",
            is_developer=False,
        )
        developer = await get_or_create_user(
            session,
            email="developer@demo.privclaw.com",
            nickname="本地开发者",
            password=DEMO_PASSWORD,
            role="developer",
            is_developer=True,
        )
        buyer = await get_or_create_user(
            session,
            email="buyer@demo.privclaw.com",
            nickname="本地买家",
            password=DEMO_PASSWORD,
            role="buyer",
            is_developer=False,
        )

        categories: list[PluginCategory] = []
        tags: list[PluginTag] = []
        plugins: dict[str, Plugin] = {}

        for spec in PLUGIN_SPECS:
            category = await get_or_create_category(
                session,
                slug=spec.category_slug,
                name=spec.category_name,
            )
            tag = await get_or_create_tag(
                session,
                slug=spec.tag_slug,
                name=spec.tag_name,
            )
            plugin = await get_or_create_plugin(
                session,
                developer=developer,
                category=category,
                tag=tag,
                spec=spec,
                storage=storage,
            )
            categories.append(category)
            tags.append(tag)
            plugins[spec.slug] = plugin

        await ensure_demo_paid_order(
            session,
            buyer=buyer,
            developer=developer,
            plugin=plugins["clawstore-demo-paid-pro"],
            order_no="DMO202603110001",
        )

        await update_demo_counters(
            session,
            developer=developer,
            categories=categories,
            tags=tags,
        )

        await session.commit()

    print("✅ Demo 数据初始化完成")
    print("")
    print("可直接登录的演示账号：")
    print(f"  admin     admin@demo.privclaw.com / {ADMIN_PASSWORD}")
    print(f"  developer developer@demo.privclaw.com / {DEMO_PASSWORD}")
    print(f"  buyer     buyer@demo.privclaw.com / {DEMO_PASSWORD}")
    print("")
    print("已准备的演示内容：")
    print("  - 1 个免费插件，可直接下单和下载")
    print("  - 1 个已售出的付费插件，可验证订单/已购/钱包")
    print("  - 1 个未购买的付费插件，可从详情页创建新订单进入支付页")


async def main() -> None:
    try:
        await seed_demo()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
