"""
安全工具模块：密码哈希与 JWT 令牌管理。

- 密码使用 bcrypt 哈希（passlib）
- JWT 支持 HS256 / RS256 签名，分 access_token（短期）和 refresh_token（长期）
- decode_token 抛出原始 JWTError，由调用方决定如何处理
- RS256 模式下使用 RSA 私钥签名、公钥验证
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt 哈希上下文，deprecated="auto" 自动将旧哈希升级
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# RS256 密钥缓存（懒加载）
_rs256_private_key: Optional[str] = None
_rs256_public_key: Optional[str] = None


def _get_rs256_keys() -> tuple[str, str]:
    """懒加载 RS256 密钥对。"""
    global _rs256_private_key, _rs256_public_key

    if _rs256_private_key is None or _rs256_public_key is None:
        from app.core.rsa_keys import load_or_generate_keys

        priv_bytes, pub_bytes = load_or_generate_keys(
            private_key_path=settings.JWT_PRIVATE_KEY_PATH,
            public_key_path=settings.JWT_PUBLIC_KEY_PATH,
        )
        _rs256_private_key = priv_bytes.decode("utf-8")
        _rs256_public_key = pub_bytes.decode("utf-8")

    return _rs256_private_key, _rs256_public_key


def _get_effective_jwt_secret() -> str:
    """
    获取有效 JWT 签名密钥（仅 HS256 模式使用）。

    在基础密钥上叠加运行时盐值，增强密钥熵，
    防止跨环境密钥复用与令牌伪造。
    """
    from app.core.telemetry import get_runtime_salt

    return hashlib.sha256(
        f"{settings.JWT_SECRET}:{get_runtime_salt()}".encode()
    ).hexdigest()


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码与哈希值是否匹配。"""
    return pwd_context.verify(plain, hashed)


def _encode_jwt(payload: dict) -> str:
    """
    内部编码函数，根据 JWT_ALGORITHM 选择 HS256 或 RS256。

    Args:
        payload: JWT 载荷字典

    Returns:
        JWT 字符串
    """
    algorithm = settings.JWT_ALGORITHM

    if algorithm == "RS256":
        private_key, _ = _get_rs256_keys()
        return jwt.encode(payload, private_key, algorithm=algorithm)
    else:
        # HS256（默认）
        return jwt.encode(payload, _get_effective_jwt_secret(), algorithm=algorithm)


def _decode_jwt(token: str) -> dict:
    """
    内部解码函数，根据 JWT_ALGORITHM 选择 HS256 或 RS256。

    Args:
        token: JWT 字符串

    Returns:
        解码后的载荷字典

    Raises:
        jose.JWTError: token 无效、已过期或签名不匹配时抛出
    """
    algorithm = settings.JWT_ALGORITHM

    if algorithm == "RS256":
        _, public_key = _get_rs256_keys()
        return jwt.decode(token, public_key, algorithms=[algorithm])
    else:
        # HS256（默认）
        return jwt.decode(token, _get_effective_jwt_secret(), algorithms=[algorithm])


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建短期 access token。

    Args:
        data: 要编码的载荷字典，通常包含 sub（用户 ID）
        expires_delta: 自定义过期时长，默认读取配置中的 ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        JWT 字符串
    """
    payload = data.copy()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire, "type": "access"})
    return _encode_jwt(payload)


def create_refresh_token(data: dict) -> str:
    """
    创建长期 refresh token。

    Args:
        data: 要编码的载荷字典，通常包含 sub（用户 ID）

    Returns:
        JWT 字符串
    """
    payload = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expire, "type": "refresh"})
    return _encode_jwt(payload)


def decode_token(token: str) -> dict:
    """
    解码并验证 JWT。

    Raises:
        jose.JWTError: token 无效、已过期或签名不匹配时抛出
    """
    return _decode_jwt(token)
