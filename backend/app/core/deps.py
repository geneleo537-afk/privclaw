"""
FastAPI 依赖注入模块。

提供当前用户解析、角色鉴权等可复用依赖函数。
每个依赖函数均可直接在路由函数的参数中通过 Depends() 注入。
"""
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.models.user import User

# auto_error=False：令牌缺失时不自动返回 403，由我们自行抛出 401
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    解析 Bearer Token，返回当前登录用户。

    Raises:
        UnauthorizedError: 令牌缺失、无效、过期，或用户被封禁时抛出
    """
    if not credentials:
        raise UnauthorizedError()

    try:
        payload = decode_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if not user_id or token_type != "access":
            raise UnauthorizedError()
    except Exception:
        raise UnauthorizedError()

    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None or user.status == "banned":
        raise UnauthorizedError("用户不存在或账号已被封禁")

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    尝试解析 Bearer Token，令牌缺失时返回 None（适用于可选登录场景）。
    """
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except UnauthorizedError:
        return None


async def require_developer(user: User = Depends(get_current_user)) -> User:
    """
    要求当前用户具有开发者或管理员身份。

    Raises:
        ForbiddenError: 角色不满足时抛出
    """
    if user.role not in ("developer", "admin"):
        raise ForbiddenError("此操作需要开发者身份")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    要求当前用户具有管理员身份。

    Raises:
        ForbiddenError: 角色不满足时抛出
    """
    if user.role != "admin":
        raise ForbiddenError("此操作需要管理员身份")
    return user
