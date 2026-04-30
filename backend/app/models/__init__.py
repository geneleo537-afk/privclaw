"""
ORM 模型包。

在此处集中导入所有模型，确保 alembic autogenerate 能发现全部表定义。
导入顺序按外键依赖排列，避免循环引用问题。
"""
from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.user import User, UserProfile
from app.models.category import PluginCategory, PluginTag
from app.models.plugin import Plugin, PluginTagRelation, PluginVersion
from app.models.order import Order, UserPurchase
from app.models.review import PluginReview
from app.models.wallet import Settlement, Transaction

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "User",
    "UserProfile",
    "PluginCategory",
    "PluginTag",
    "Plugin",
    "PluginTagRelation",
    "PluginVersion",
    "Order",
    "UserPurchase",
    "PluginReview",
    "Transaction",
    "Settlement",
]
