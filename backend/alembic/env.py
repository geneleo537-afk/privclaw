"""
Alembic 异步迁移环境配置。

使用 asyncpg 驱动的异步 SQLAlchemy 引擎（async_engine_from_config），
通过 run_sync() 适配器在异步连接上执行同步 DDL 回调，无需替换驱动。
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 导入所有模型，确保 autogenerate 能发现全部表
from app.core.config import settings
from app.models.base import Base
from app.models import (  # noqa: F401  触发所有模型注册
    user,
    category,
    plugin,
    order,
    wallet,
)

# Alembic Config 对象，提供对 .ini 文件值的访问
config = context.config

# 直接使用 asyncpg URL：async_engine_from_config 本身支持 asyncpg 异步驱动，
# 通过 run_sync() 在异步连接上执行 DDL，无需切换成 psycopg2 同步驱动。
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 配置 Python logging（来自 alembic.ini 的 [loggers] 节）
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 将 metadata 指向所有模型的 Base，支持 autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：直接将 SQL 输出到标准输出或文件，不需要真实数据库连接。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 对比迁移时忽略的对象类型（如序列、扩展等）
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """在给定连接上执行实际迁移。"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在线模式：创建异步引擎，通过同步适配器执行迁移。"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync 将同步回调在异步连接上执行
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口：启动异步事件循环执行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
