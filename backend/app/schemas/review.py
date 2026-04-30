"""
评价相关 Schema：创建请求、响应体、汇总信息。
"""
import uuid
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    """创建评价请求体。"""

    rating: int = Field(ge=1, le=5, description="评分 1-5")
    title: str = Field(default="", max_length=200, description="评价标题")
    content: str = Field(default="", max_length=5000, description="评价内容")


class ReviewResponse(BaseModel):
    """单条评价响应体。"""

    id: uuid.UUID
    plugin_id: uuid.UUID
    user_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    rating: int
    title: str
    content: str
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    user_nickname: str = ""
    user_avatar_url: str = ""

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    """评价汇总信息。"""

    avg_rating: float = 0.0
    rating_count: int = 0
    rating_distribution: Dict[int, int] = Field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    )
