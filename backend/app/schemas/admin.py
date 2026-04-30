"""
管理后台相关 Schema：仪表盘、插件状态变更、用户封禁、提现审核、退款、趋势。
"""
from typing import List, Optional

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    """管理后台仪表盘统计响应体。"""

    total_users: int
    total_plugins: int
    total_orders: int
    total_revenue: float
    pending_withdrawals: int
    today_orders: int = 0
    today_revenue: float = 0.0
    today_new_users: int = 0
    pending_reviews: int = 0


class TrendDataPoint(BaseModel):
    """管理员趋势数据单点。"""

    date: str
    order_count: int = 0
    revenue: float = 0.0
    new_users: int = 0


class TrendResponse(BaseModel):
    """管理员趋势数据响应。"""

    points: List[TrendDataPoint]


class DeveloperTrendDataPoint(BaseModel):
    """开发者趋势数据单点。"""

    date: str
    sales_count: int = 0
    revenue: float = 0.0


class DeveloperTrendResponse(BaseModel):
    """开发者趋势数据响应。"""

    points: List[DeveloperTrendDataPoint]


class UpdatePluginStatusRequest(BaseModel):
    """管理员变更插件状态请求体。"""

    # 合法值：published / suspended / draft / removed
    status: str
    reason: Optional[str] = None


class BanUserRequest(BaseModel):
    """管理员封禁/解封用户请求体。"""

    # 合法值：ban / unban
    action: str
    reason: Optional[str] = None


class ApproveWithdrawalRequest(BaseModel):
    """管理员批准提现请求体。"""

    note: Optional[str] = None


class RejectWithdrawalRequest(BaseModel):
    """管理员拒绝提现请求体（必须说明原因）。"""

    reason: str


class RefundOrderRequest(BaseModel):
    """管理员退款请求体（必须说明原因）。"""

    reason: str
