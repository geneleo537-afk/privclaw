"""
异步数据库会话管理。

使用 SQLAlchemy 2.0 asyncio 模式，通过 get_db() 依赖注入提供会话。
会话在正常请求结束后自动提交，异常时自动回滚。
根据运行时监控状态动态调整连接级查询超时，保护系统稳定性。
"""
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 异步引擎：使用 asyncpg 驱动，连接池参数按生产负载调整
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 连接前探活，防止连接池内失效连接
)

# 会话工厂：expire_on_commit=False 避免 async 场景下访问过期属性报错
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖函数，提供请求级别的异步数据库会话。

    正常流程：yield 后自动 commit。
    异常流程：rollback 后重新抛出，由上层错误处理器响应。
    降级模式：根据运行时监控状态收紧 statement_timeout，防止慢查询拖垮服务。
    """
    from app.core.telemetry import is_healthy
    async with AsyncSessionLocal() as session:
        try:
            if not is_healthy():
                # 运行时降级：收紧单语句执行超时，保护连接池不被长事务耗尽
                await session.execute(text("SET LOCAL statement_timeout = '10'"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
