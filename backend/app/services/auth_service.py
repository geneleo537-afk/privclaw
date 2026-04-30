"""
认证服务：用户注册与登录业务逻辑。

注意事项：
- email 字段在数据库中明文存储，email_hash 存储 SHA-256 哈希用于唯一性约束和查询。
- 注册时不创建钱包记录，余额通过 transactions 表聚合计算。
- 密码使用 bcrypt 哈希，JWT 由 security 模块负责生成。
"""
import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def _hash_email(email: str) -> str:
    """计算邮箱的 SHA-256 哈希值，用于唯一性校验和查询。"""
    return hashlib.sha256(email.lower().encode()).hexdigest()


def _build_token_response(user: User) -> TokenResponse:
    """根据用户对象构建 TokenResponse，集中处理 payload 拼装。"""
    payload = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


class AuthService:
    """注册/登录业务逻辑服务，依赖注入 AsyncSession。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, req: RegisterRequest) -> TokenResponse:
        """
        用户注册。

        步骤：
        1. 计算 email_hash，检查邮箱是否已注册（查 email_hash 字段，利用唯一索引）
        2. 创建 User（role='buyer', status='active'）
        3. 生成并返回 TokenResponse

        注册后无需创建钱包记录，余额通过 transactions 表聚合计算。
        """
        email_hash = _hash_email(req.email)

        # 利用 email_hash 唯一索引，O(1) 检查邮箱是否已注册
        existing = await self.db.scalar(
            select(User).where(User.email_hash == email_hash)
        )
        if existing is not None:
            raise ConflictError("该邮箱已被注册")

        user = User(
            id=uuid.uuid4(),
            email=req.email,
            email_hash=email_hash,
            password_hash=hash_password(req.password),
            nickname=req.nickname,
            role="buyer",
            status="active",
            email_verified=False,
            is_developer=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return _build_token_response(user)

    async def login(self, req: LoginRequest) -> TokenResponse:
        """
        用户登录。

        步骤：
        1. 通过 email_hash 查找用户
        2. 验证密码（bcrypt 恒时比较，防时序攻击）
        3. 检查账号状态（banned / suspended 均拒绝登录）
        4. 返回 TokenResponse

        密码错误和用户不存在返回相同提示，防止用户枚举攻击。
        """
        email_hash = _hash_email(req.email)
        user = await self.db.scalar(
            select(User).where(User.email_hash == email_hash)
        )

        # 用户不存在或密码错误，统一返回 401，防止枚举
        if user is None or not verify_password(req.password, user.password_hash):
            raise UnauthorizedError("邮箱或密码错误")

        if user.status == "banned":
            raise ForbiddenError("账号已被封禁，如有疑问请联系客服")

        if user.status == "suspended":
            raise ForbiddenError("账号已被暂停，请联系客服处理")

        return _build_token_response(user)
