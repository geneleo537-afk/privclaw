"""
RSA 密钥管理工具。

负责 RS256 JWT 签名所需的 RSA 密钥对加载与生成：
- 从 PEM 文件加载私钥/公钥
- 密钥不存在时自动生成 2048 位 RSA 密钥对
"""
import os
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def _ensure_key_dir(key_path: Path) -> None:
    """确保密钥文件所在目录存在。"""
    key_path.parent.mkdir(parents=True, exist_ok=True)


def _generate_rsa_keys(private_path: Path, public_path: Path) -> None:
    """生成 2048 位 RSA 密钥对并写入 PEM 文件。"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    _ensure_key_dir(private_path)
    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)


def load_or_generate_keys(
    private_key_path: str,
    public_key_path: str,
) -> tuple:
    """
    加载 RSA 密钥对，若文件不存在则自动生成。

    Returns:
        (private_key_pem: bytes, public_key_pem: bytes)
    """
    priv_path = Path(private_key_path)
    pub_path = Path(public_key_path)

    if not priv_path.exists() or not pub_path.exists():
        _generate_rsa_keys(priv_path, pub_path)

    return priv_path.read_bytes(), pub_path.read_bytes()
