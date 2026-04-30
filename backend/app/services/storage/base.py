"""
对象存储抽象基类。

所有存储后端（MinIO、阿里云 OSS 等）必须实现此接口，
业务层通过抽象类调用，不依赖具体 SDK，便于按环境切换存储后端。
"""
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """对象存储后端抽象接口。"""

    @abstractmethod
    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件到对象存储。

        Args:
            key:          存储路径（如 "plugins/uuid/1.0.0/plugin.zip"）
            data:         文件二进制内容
            content_type: MIME 类型，默认 application/octet-stream

        Returns:
            文件 key（与传入的 key 相同，便于调用方存储引用）
        """

    @abstractmethod
    async def get_presigned_url(self, key: str, expires: int = 300) -> str:
        """
        生成文件临时下载链接（预签名 URL）。

        Args:
            key:     文件存储路径
            expires: 链接有效期（秒），默认 300 秒（5 分钟）

        Returns:
            带时效签名的下载 URL，过期后自动失效
        """

    @abstractmethod
    async def get_object(self, key: str) -> tuple[bytes, str]:
        """
        获取文件二进制内容。

        Returns:
            (data, content_type) 元组
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        删除存储中的文件。

        Args:
            key: 文件存储路径

        注意：文件不存在时不抛异常（幂等删除）。
        """
