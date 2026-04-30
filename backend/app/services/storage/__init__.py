"""
对象存储后端工厂。

按环境变量选择 MinIO 或 OSS，并在进程内复用单例实例，
避免每次请求重复初始化 SDK 客户端。
"""
from app.core.config import settings
from app.services.storage.base import StorageBackend
from app.services.storage.minio_backend import MinIOBackend
from app.services.storage.oss_backend import OSSBackend

_storage_backend: StorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """返回当前环境对应的对象存储后端实例。"""
    global _storage_backend

    if _storage_backend is None:
        if settings.STORAGE_BACKEND == "oss":
            _storage_backend = OSSBackend()
        else:
            _storage_backend = MinIOBackend()

    return _storage_backend


__all__ = [
    "StorageBackend",
    "get_storage_backend",
]
