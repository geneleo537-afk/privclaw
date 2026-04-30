"""
认证相关接口：注册、登录、退出、刷新令牌。

POST /auth/register  — 邮箱注册，创建 User + UserProfile
POST /auth/login     — 邮箱密码登录，返回双 token
POST /auth/logout    — 退出登录（当前为无状态实现，后续加 token 黑名单）
POST /auth/refresh   — 用 refresh_token 换取新 access_token
"""
import hashlib
import uuid

from fastapi import APIRouter, Depends
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserProfile
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.common import Response

router = APIRouter()


def _email_hash(email: str) -> str:
    """对邮箱小写后取 SHA-256 哈希，用于唯一性校验和登录查询。"""
    return hashlib.sha256(email.lower().encode()).hexdigest()


@router.post(
    "/register",
    response_model=Response[TokenResponse],
    status_code=201,
    summary="用户注册",
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Response[TokenResponse]:
    """
    邮箱注册新账号。

    - 检查邮箱是否已注册（通过 email_hash 查询，避免解密开销）
    - bcrypt 哈希密码
    - 创建 User 记录和对应的 UserProfile 记录
    - 注册成功后直接返回双 token，无需额外登录步骤
    """
    email_hash = _email_hash(body.email)

    # 检查邮箱唯一性
    existing = await db.execute(
        select(User).where(User.email_hash == email_hash)
    )
    if existing.scalar_one_or_none():
        raise ConflictError("该邮箱已注册")

    # 创建用户（email 字段在完整实现中应使用 pgcrypto 加密，
    # 此处为骨架阶段直接存储明文，生产环境必须加密）
    user = User(
        id=uuid.uuid4(),
        email=body.email,
        email_hash=email_hash,
        password_hash=hash_password(body.password),
        nickname=body.nickname,
        role="buyer",
        status="active",
    )
    db.add(user)
    await db.flush()  # 获取 user.id，但不提交事务

    # 同步创建扩展资料
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user.id,
    )
    db.add(profile)
    # 事务由 get_db 依赖在请求结束后统一提交

    # 生成双 token
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Response.ok(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        message="注册成功",
    )


@router.post(
    "/login",
    response_model=Response[TokenResponse],
    summary="用户登录",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Response[TokenResponse]:
    """
    邮箱密码登录。

    - 通过 email_hash 定位用户，避免遍历解密
    - bcrypt 验证密码
    - 检查账号状态（banned 账号拒绝登录）
    - 返回 access_token + refresh_token
    """
    email_hash = _email_hash(body.email)

    result = await db.execute(
        select(User).where(User.email_hash == email_hash, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    # 用户不存在或密码错误，统一返回相同错误信息（防止用户枚举）
    if not user or not verify_password(body.password, user.password_hash):
        raise BadRequestError("邮箱或密码错误")

    if user.status == "banned":
        raise BadRequestError("账号已被封禁，请联系客服")

    if user.status == "suspended":
        raise BadRequestError("账号已被暂停，请联系客服")

    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Response.ok(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        message="登录成功",
    )


@router.post(
    "/logout",
    response_model=Response[None],
    summary="退出登录",
)
async def logout() -> Response[None]:
    """
    退出登录。

    当前为无状态实现，客户端删除本地 token 即可。
    后续版本将引入 Redis token 黑名单，在服务端强制失效 token。
    """
    return Response.ok(message="已退出登录")


@router.post(
    "/refresh",
    response_model=Response[TokenResponse],
    summary="刷新 access_token",
)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Response[TokenResponse]:
    """
    使用 refresh_token 换取新的 access_token。

    - 验证 refresh_token 有效性和类型
    - 确认用户仍然存在且未被封禁
    - 返回新的 access_token（refresh_token 不轮换，客户端继续使用原来的）
    """
    try:
        payload = decode_token(body.refresh_token)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if not user_id or token_type != "refresh":
            raise UnauthorizedError("无效的刷新令牌")
    except JWTError:
        raise UnauthorizedError("令牌已过期或无效")

    result = await db.execute(
        select(User).where(
            User.id == uuid.UUID(user_id),
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if not user or user.status in ("banned", "suspended"):
        raise UnauthorizedError("用户不存在或账号状态异常")

    token_data = {"sub": str(user.id)}
    new_access_token = create_access_token(token_data)

    return Response.ok(
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=body.refresh_token,  # refresh_token 保持不变
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        message="令牌刷新成功",
    )
