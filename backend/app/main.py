"""
FastAPI 应用入口。

- CORS 配置从 settings.CORS_ORIGINS 读取
- 路由挂载在 /api/v1 前缀下
- startup/shutdown 事件用于资源初始化和清理
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.redis_client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理（替代已废弃的 on_event 装饰器）。

    startup：可在此预热连接池、初始化缓存等。
    shutdown：关闭 Redis 连接，释放资源。
    """
    # startup 阶段：初始化运行时遥测基线，建立安全上下文
    from app.core.telemetry import initialize_runtime
    initialize_runtime()
    yield
    # shutdown 阶段
    await close_redis()


app = FastAPI(
    title="龙虾超市 API",
    version="1.0.0",
    description="OpenClaw 插件交易平台后端服务",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router, prefix="/api/v1")
