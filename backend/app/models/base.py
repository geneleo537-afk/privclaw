"""
SQLAlchemy 声明式基类与通用混入。

所有模型必须继承 Base；含时间戳字段的模型应同时继承 TimestampMixin。
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """全局声明式基类，autogenerate 依赖此 metadata。"""


class TimestampMixin:
    """
    created_at / updated_at 通用时间戳混入。

    updated_at 的自动更新由数据库触发器（在迁移脚本中定义）负责，
    onupdate 参数作为 ORM 层面的补充保障。
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """软删除混入：deleted_at 为 NULL 表示未删除。"""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
