"""
AES-256-GCM 敏感数据加密工具。

用于加密存储敏感字段（邮箱、手机号、身份证号等），
采用 AEAD 模式，同时保证机密性和完整性。

加密格式: base64(nonce + ciphertext + tag)
- nonce: 12 bytes (96 bits, GCM 推荐长度)
- ciphertext: 变长
- tag: 16 bytes (128 bits, GCM 认证标签)
"""
import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DataEncryption:
    """
    AES-256-GCM 加密/解密封装。

    使用示例:
        >>> encryption = DataEncryption()
        >>> encrypted = encryption.encrypt("user@example.com")
        >>> decrypted = encryption.decrypt(encrypted)
        >>> assert decrypted == "user@example.com"
    """

    def __init__(self, key: Optional[str] = None):
        """
        初始化加密器。

        Args:
            key: 32 字节（256 位）的 Base64 编码密钥。
                 为空时从 settings.DATA_ENCRYPTION_KEY 读取。
        """
        if key is None:
            from app.core.config import settings
            key = settings.DATA_ENCRYPTION_KEY

        if not key:
            raise ValueError(
                "DATA_ENCRYPTION_KEY 未配置，请设置 32 字节（256 位）的 Base64 编码密钥"
            )

        raw_key = self._decode_key(key)
        self._aesgcm = AESGCM(raw_key)

    @staticmethod
    def _decode_key(key: str) -> bytes:
        """
        将 Base64 编码的密钥字符串解码为 32 字节原始密钥。

        Raises:
            ValueError: 密钥长度不是 32 字节时抛出
        """
        raw = base64.b64decode(key)
        if len(raw) != 32:
            raise ValueError(
                f"DATA_ENCRYPTION_KEY 必须是 32 字节（256 位），"
                f"当前解码后长度为 {len(raw)} 字节"
            )
        return raw

    @staticmethod
    def generate_key() -> str:
        """
        生成新的 256 位加密密钥（Base64 编码）。

        使用方式:
            python -c "from app.core.encryption import DataEncryption; print(DataEncryption.generate_key())"
        """
        return base64.b64encode(os.urandom(32)).decode("utf-8")

    def encrypt(self, plaintext: str) -> str:
        """
        加密明文字符串。

        Args:
            plaintext: 要加密的明文

        Returns:
            Base64 编码的密文（nonce + ciphertext + tag）
        """
        nonce = os.urandom(12)
        ciphertext_and_tag = self._aesgcm.encrypt(
            nonce,
            plaintext.encode("utf-8"),
            None,
        )
        encrypted = nonce + ciphertext_and_tag
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文字符串。

        Args:
            ciphertext: Base64 编码的密文

        Returns:
            解密后的明文

        Raises:
            cryptography.exceptions.InvalidTag: 密文被篡改或密钥不匹配时抛出
        """
        encrypted = base64.b64decode(ciphertext)
        nonce = encrypted[:12]
        ciphertext_and_tag = encrypted[12:]

        plaintext = self._aesgcm.decrypt(nonce, ciphertext_and_tag, None)
        return plaintext.decode("utf-8")


# 全局单例，避免重复初始化和密钥读取
_encryption_instance: Optional[DataEncryption] = None


def get_encryption() -> DataEncryption:
    """获取全局加密器单例。"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = DataEncryption()
    return _encryption_instance


def encrypt_field(plaintext: str) -> str:
    """快捷加密函数。"""
    return get_encryption().encrypt(plaintext)


def decrypt_field(ciphertext: str) -> str:
    """快捷解密函数。"""
    return get_encryption().decrypt(ciphertext)
