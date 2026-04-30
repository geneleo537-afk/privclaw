"""
MinIO 对象存储后端实现。

使用官方 minio-py SDK（minio==7.x）：
- upload：使用 put_object 上传二进制数据
- get_presigned_url：使用 presigned_get_object 生成临时链接
- delete：使用 remove_object 删除文件

注意：
- MinIO Python SDK 目前不提供原生异步客户端，同步操作在异步方法内调用。
  对于高并发场景，建议通过 asyncio.get_event_loop().run_in_executor 包装，
  此处为直接调用，适用于文件上传/下载频率较低的插件市场场景。
- _ensure_bucket 在构造时同步执行，应用启动时完成 bucket 初始化。
"""
import datetime
import io
import logging

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class MinIOBackend(StorageBackend):
    """MinIO 对象存储后端。"""

    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """确保 bucket 存在，不存在时自动创建（应用启动时执行一次）。"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("MinIO bucket '%s' 已创建", self.bucket)
        except S3Error as e:
            logger.error("MinIO bucket 初始化失败：%s", e)
            raise

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件到 MinIO。

        Args:
            key:          对象路径（如 plugins/uuid/1.0.0/file.zip）
            data:         文件二进制内容
            content_type: MIME 类型

        Returns:
            存储路径 key（与传入值相同）
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except S3Error as e:
            logger.error("MinIO 上传失败，key=%s，error=%s", key, e)
            raise
        return key

    async def get_presigned_url(self, key: str, expires: int = 300) -> str:
        """
        生成 MinIO 预签名下载 URL。

        若配置了 MINIO_EXTERNAL_ENDPOINT，自动将 URL 中的内部地址替换为外部地址，
        使浏览器可直接访问。
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=key,
                expires=datetime.timedelta(seconds=expires),
            )
        except S3Error as e:
            logger.error("MinIO 预签名 URL 生成失败，key=%s，error=%s", key, e)
            raise

        # 将容器内部地址替换为外部可访问地址
        external = settings.MINIO_EXTERNAL_ENDPOINT
        if external and external != settings.MINIO_ENDPOINT:
            url = url.replace(settings.MINIO_ENDPOINT, external, 1)

        return url

    async def get_object(self, key: str) -> tuple[bytes, str]:
        """从 MinIO 获取文件二进制内容。"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=key,
            )
            data = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            response.close()
            response.release_conn()
            return data, content_type
        except S3Error as e:
            logger.error("MinIO 获取文件失败，key=%s，error=%s", key, e)
            raise

    async def delete(self, key: str) -> None:
        """
        删除 MinIO 中的对象（幂等，不存在时不抛异常）。

        Args:
            key: 对象路径
        """
        try:
            self.client.remove_object(bucket_name=self.bucket, object_name=key)
        except S3Error as e:
            # NoSuchKey 表示文件不存在，幂等处理静默忽略
            if e.code == "NoSuchKey":
                logger.debug("MinIO 删除：对象不存在，key=%s", key)
                return
            logger.error("MinIO 删除失败，key=%s，error=%s", key, e)
            raise
