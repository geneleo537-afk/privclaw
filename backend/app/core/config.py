"""
应用配置模块。

使用 pydantic-settings 从环境变量或 .env 文件读取配置，
所有密钥和连接串必须通过环境变量注入，禁止硬编码生产凭证。
"""
import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─── 应用基础 ──────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "dev-secret-change-in-production"

    # ─── 数据库 ────────────────────────────────────────────────────────────
    # 格式：postgresql+asyncpg://user:pass@host:port/dbname
    DATABASE_URL: str

    # ─── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── JWT 认证 ───────────────────────────────────────────────────────────
    JWT_SECRET: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"  # "HS256" | "RS256"
    JWT_PRIVATE_KEY_PATH: str = "keys/jwt_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "keys/jwt_public.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── 敏感数据加密 ───────────────────────────────────────────────────────
    DATA_ENCRYPTION_KEY: str = ""

    # ─── 对象存储（MinIO 开发 / 阿里云 OSS 生产）──────────────────────────
    STORAGE_BACKEND: str = "minio"  # "minio" | "oss"
    # MinIO（开发环境）
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "privclaw"
    MINIO_USE_SSL: bool = False
    MINIO_EXTERNAL_ENDPOINT: str = ""  # 外部可访问地址，为空时与 MINIO_ENDPOINT 相同
    # 阿里云 OSS（生产环境，切换 STORAGE_BACKEND=oss 时生效）
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"
    OSS_BUCKET: str = ""
    OSS_CDN_DOMAIN: str = ""  # 可选 CDN 域名，空字符串表示不使用 CDN

    # ─── 支付宝支付 ────────────────────────────────────────────────────────
    ALIPAY_APP_ID: str = ""
    ALIPAY_PID: str = ""
    ALIPAY_GATEWAY: str = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_NOTIFY_URL: str = ""

    # ─── Celery 异步任务 ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── 业务参数 ───────────────────────────────────────────────────────────
    WITHDRAW_MIN_AMOUNT: float = 100.0
    WITHDRAW_COOLDOWN_DAYS: int = 7
    PLATFORM_FEE_RATE: float = 0.30

    # ─── CORS ──────────────────────────────────────────────────────────────
    # 环境变量中可传 JSON 字符串，如：'["http://localhost:3000"]'
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        """支持从环境变量中传入 JSON 字符串形式的 CORS 列表。"""
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = {
        "env_file": ".env.dev",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

if settings.APP_ENV != "development":
    _defaults = {
        "APP_SECRET_KEY": "dev-secret-change-in-production",
        "JWT_SECRET": "dev-jwt-secret-change-in-production",
    }
    for _key, _default in _defaults.items():
        if getattr(settings, _key) == _default:
            raise RuntimeError(f"安全错误：{_key} 仍使用默认值，请在 .env 中设置安全密钥")
