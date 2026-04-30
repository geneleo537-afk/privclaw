"""
用户相关 Schema：个人信息响应、更新请求。
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """用户信息响应体（公开字段，不含敏感信息）。"""

    id: uuid.UUID
    email: str = Field(description="登录邮箱（已脱敏）")
    nickname: str
    avatar_url: str
    role: str
    status: str
    email_verified: bool
    is_developer: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    """更新用户个人资料请求体（所有字段可选，仅更新提供的字段）。"""

    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="昵称")
    avatar_url: Optional[str] = Field(None, max_length=512, description="头像 URL")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    website: Optional[str] = Field(None, max_length=512, description="个人网站")
    github_url: Optional[str] = Field(None, max_length=512, description="GitHub 主页")
    company: Optional[str] = Field(None, max_length=200, description="所属公司/组织")


class UserDetailResponse(UserResponse):
    """用户详细信息响应体（包含扩展资料，适用于用户本人查看自己的资料）。"""

    bio: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    company: Optional[str] = None
    last_login_at: Optional[datetime] = None
