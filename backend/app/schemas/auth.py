"""
认证相关 Schema：注册、登录、令牌响应、刷新令牌。
"""
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """用户注册请求体。"""

    email: EmailStr = Field(description="登录邮箱")
    password: str = Field(min_length=8, max_length=128, description="密码（8-128 字符）")
    nickname: str = Field(min_length=1, max_length=50, description="昵称")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """密码强度校验：至少包含字母和数字。"""
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v

    @field_validator("nickname")
    @classmethod
    def nickname_no_spaces(cls, v: str) -> str:
        """昵称不允许首尾空白。"""
        stripped = v.strip()
        if not stripped:
            raise ValueError("昵称不能为空")
        return stripped


class LoginRequest(BaseModel):
    """用户登录请求体。"""

    email: EmailStr = Field(description="登录邮箱")
    password: str = Field(min_length=8, max_length=128, description="密码（8-128 字符）")


class TokenResponse(BaseModel):
    """令牌响应，包含 access_token 和 refresh_token。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="access_token 有效期（秒）")


class RefreshRequest(BaseModel):
    """刷新令牌请求体。"""

    refresh_token: str = Field(description="有效的 refresh_token")
