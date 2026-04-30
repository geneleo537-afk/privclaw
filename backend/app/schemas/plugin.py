"""
插件相关 Schema：列表项、详情响应、创建请求。
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class PluginListItem(BaseModel):
    """插件列表项（轻量数据，适用于列表页展示）。"""

    id: uuid.UUID
    name: str
    slug: str
    summary: str
    icon_url: str
    price: Decimal
    is_free: bool
    status: str
    current_version: str
    download_count: int
    avg_rating: Decimal
    rating_count: int
    developer_id: uuid.UUID
    developer_nickname: str = ""
    category_name: Optional[str] = None
    category_slug: Optional[str] = None

    model_config = {"from_attributes": True}


class PluginResponse(BaseModel):
    """插件详情响应（完整数据，适用于详情页）。"""

    id: uuid.UUID
    name: str
    slug: str
    summary: str
    description: str
    icon_url: str
    screenshots: list
    price: Decimal
    currency: str
    is_free: bool
    status: str
    review_status: str
    current_version: str
    current_version_id: Optional[uuid.UUID]
    download_count: int
    purchase_count: int
    avg_rating: Decimal
    rating_count: int
    developer_id: uuid.UUID
    developer_nickname: str = ""
    category_id: Optional[uuid.UUID]
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="标签名称列表")
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreatePluginRequest(BaseModel):
    """创建插件请求体。"""

    name: str = Field(min_length=1, max_length=200, description="插件名称")
    summary: str = Field(max_length=500, description="一句话简介")
    description: str = Field(default="", description="详细描述（Markdown）")
    icon_url: str = Field(default="", max_length=512, description="插件图标 URL")
    price: Decimal = Field(default=Decimal("0.00"), ge=0, description="价格，0=免费")
    category_id: Optional[uuid.UUID] = Field(None, description="分类 ID")
    tag_ids: List[uuid.UUID] = Field(default_factory=list, description="标签 ID 列表")


class UpdatePluginRequest(BaseModel):
    """更新插件请求体（所有字段可选）。"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=512)
    price: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[uuid.UUID] = None
    tag_ids: Optional[List[uuid.UUID]] = None
