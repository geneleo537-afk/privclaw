"""
阿里云 OSS 对象存储后端实现。

使用 oss2 SDK（oss2==2.18.6）：
- upload：oss2.Bucket.put_object 上传
- get_presigned_url：oss2.Bucket.sign_url 生成临时链接
- delete：oss2.Bucket.delete_object 删除

前置配置（需在 config.py / .env 中补充以下环境变量）：
- OSS_ACCESS_KEY_ID     : 阿里云 RAM 访问密钥 ID
- OSS_ACCESS_KEY_SECRET : 阿里云 RAM 访问密钥 Secret
- OSS_ENDPOINT          : OSS 区域 Endpoint（如 oss-cn-hangzhou.aliyuncs.com）
- OSS_BUCKET            : Bucket 名称

注意：
- oss2 SDK 为同步客户端，在异步方法中直接调用。
  插件市场上传/下载频率不高，当前实现可满足需求。
  如需高并发，后续可通过 run_in_executor 包装为非阻塞调用。
- headers 中设置 Content-Type 确保浏览器正确识别文件类型。
"""
import logging

import oss2

from app.core.config import settings
from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class OSSBackend(StorageBackend):
    """阿里云 OSS 对象存储后端。"""

    def __init__(self) -> None:
        # 从 settings 读取 OSS 配置（需在 config.py 和 .env 中添加对应字段）
        access_key_id: str = getattr(settings, "OSS_ACCESS_KEY_ID", "")
        access_key_secret: str = getattr(settings, "OSS_ACCESS_KEY_SECRET", "")
        endpoint: str = getattr(settings, "OSS_ENDPOINT", "")
        bucket_name: str = getattr(settings, "OSS_BUCKET", "")

        if not all([access_key_id, access_key_secret, endpoint, bucket_name]):
            raise RuntimeError(
                "OSSBackend 配置不完整，请在环境变量中设置 "
                "OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET / OSS_ENDPOINT / OSS_BUCKET"
            )

        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件到阿里云 OSS。

        Args:
            key:          对象路径（如 plugins/uuid/1.0.0/file.zip）
            data:         文件二进制内容
            content_type: MIME 类型

        Returns:
            存储路径 key（与传入值相同）
        """
        headers = {"Content-Type": content_type}
        try:
            self.bucket.put_object(key, data, headers=headers)
        except oss2.exceptions.OssError as e:
            logger.error("OSS 上传失败，key=%s，error=%s", key, e)
            raise
        return key

    async def get_presigned_url(self, key: str, expires: int = 300) -> str:
        """
        生成 OSS 临时下载 URL（预签名）。

        Args:
            key:     对象路径
            expires: 有效期（秒），默认 300 秒

        Returns:
            带签名的临时下载 URL
        """
        try:
            url = self.bucket.sign_url("GET", key, expires)
        except oss2.exceptions.OssError as e:
            logger.error("OSS 预签名 URL 生成失败，key=%s，error=%s", key, e)
            raise
        return url

    async def get_object(self, key: str) -> tuple[bytes, str]:
        """从 OSS 获取文件二进制内容。"""
        try:
            result = self.bucket.get_object(key)
            data = result.read()
            content_type = result.headers.get("Content-Type", "application/octet-stream")
            return data, content_type
        except oss2.exceptions.OssError as e:
            logger.error("OSS 获取文件失败，key=%s，error=%s", key, e)
            raise

    async def delete(self, key: str) -> None:
        """
        删除 OSS 中的对象（幂等，不存在时不抛异常）。

        Args:
            key: 对象路径
        """
        try:
            self.bucket.delete_object(key)
        except oss2.exceptions.NoSuchKey:
            # 幂等：文件不存在时静默忽略
            logger.debug("OSS 删除：对象不存在，key=%s", key)
        except oss2.exceptions.OssError as e:
            logger.error("OSS 删除失败，key=%s，error=%s", key, e)
            raise
