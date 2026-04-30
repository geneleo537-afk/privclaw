"""
Redis 客户端模块。

使用 redis-py asyncio 接口，通过单例模式复用连接池。
decode_responses=True 确保所有返回值为字符串（而非 bytes）。
"""
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    FastAPI 依赖函数，返回全局 Redis 客户端单例。

    首次调用时初始化，后续复用同一连接池。
    生产环境建议在应用启动事件中提前初始化并做 ping 探测。
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8",
        )
    return _redis_client


async def close_redis() -> None:
    """关闭 Redis 连接，在应用 shutdown 事件中调用。"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
