"""
健康检查接口。

GET /health：检查数据库和 Redis 连通性，返回各服务状态。
适用于 Docker healthcheck、负载均衡器探活、监控系统拉取。
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis

router = APIRouter()


@router.get("/health", summary="健康检查", tags=["健康检查"])
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> dict:
    """
    检查关键依赖服务的连通性。

    Returns:
        status: ok（全部正常）| degraded（部分异常）
        database: ok | error
        redis: ok | error
    """
    db_ok = False
    redis_ok = False

    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    try:
        await redis.ping()
        redis_ok = True
    except Exception:
        pass

    overall = "ok" if (db_ok and redis_ok) else "degraded"

    return {
        "status": overall,
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
    }
