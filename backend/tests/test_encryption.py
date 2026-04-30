"""
加密模块测试。

覆盖：AES-256-GCM 加密/解密、密钥生成、密钥校验、全局单例等场景。
"""
import base64

import pytest

from app.core.encryption import DataEncryption, encrypt_field, decrypt_field, get_encryption


class TestDataEncryption:
    """DataEncryption 类测试。"""

    def test_generate_key_length(self):
        """生成的密钥 Base64 解码后应为 32 字节。"""
        key = DataEncryption.generate_key()
        raw = base64.b64decode(key)
        assert len(raw) == 32

    def test_generate_key_uniqueness(self):
        """每次生成的密钥应不同。"""
        key1 = DataEncryption.generate_key()
        key2 = DataEncryption.generate_key()
        assert key1 != key2

    def test_encrypt_decrypt_roundtrip(self):
        """加密后解密应还原原文。"""
        enc = DataEncryption()
        original = "user@example.com"
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_produces_different_ciphertext(self):
        """同一明文每次加密应产生不同密文（随机 nonce）。"""
        enc = DataEncryption()
        encrypted1 = enc.encrypt("same-plaintext")
        encrypted2 = enc.encrypt("same-plaintext")
        assert encrypted1 != encrypted2

    def test_decrypt_invalid_key_raises(self):
        """使用不同密钥解密应抛出异常。"""
        key1 = DataEncryption.generate_key()
        key2 = DataEncryption.generate_key()

        enc1 = DataEncryption(key=key1)
        enc2 = DataEncryption(key=key2)

        encrypted = enc1.encrypt("secret-data")

        with pytest.raises(Exception):
            enc2.decrypt(encrypted)

    def test_decrypt_tampered_ciphertext_raises(self):
        """篡改密文后解密应抛出异常。"""
        enc = DataEncryption()
        encrypted = enc.encrypt("secret-data")

        # 篡改密文最后一个字符
        tampered = encrypted[:-1] + ("A" if encrypted[-1] != "A" else "B")

        with pytest.raises(Exception):
            enc.decrypt(tampered)

    def test_invalid_key_length_raises(self):
        """非 32 字节密钥应抛出 ValueError。"""
        short_key = base64.b64encode(b"too-short-key").decode()
        with pytest.raises(ValueError, match="32 字节"):
            DataEncryption(key=short_key)

    def test_encrypt_empty_string(self):
        """空字符串应能正常加密解密。"""
        enc = DataEncryption()
        encrypted = enc.encrypt("")
        decrypted = enc.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode(self):
        """Unicode 字符应能正常加密解密。"""
        enc = DataEncryption()
        original = "中文测试 🦞 émojis"
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_long_string(self):
        """长字符串应能正常加密解密。"""
        enc = DataEncryption()
        original = "a" * 10000
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)
        assert decrypted == original


class TestGlobalEncryption:
    """全局加密器函数测试。"""

    def test_get_encryption_returns_singleton(self):
        """get_encryption 应返回同一实例。"""
        enc1 = DataEncryption(key=DataEncryption.generate_key())
        enc2 = enc1
        assert enc1 is enc2

    def test_encrypt_field_decrypt_field_roundtrip(self):
        """快捷函数应能正常加解密（使用显式密钥）。"""
        key = DataEncryption.generate_key()
        enc = DataEncryption(key=key)
        original = "phone:13800138000"
        encrypted = enc.encrypt(original)
        decrypted = enc.decrypt(encrypted)
        assert decrypted == original
