"""
API v1 路由总线。

所有子模块路由在此注册，通过 prefix="/api/v1" 挂载到主应用。
新增路由模块时，在此文件添加 include_router 调用。
"""
from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    categories,
    health,
    orders,
    payments,
    plugins,
    reviews,
    users,
    wallet,
)

api_router = APIRouter()

# 健康检查（无 prefix，直接挂载在 /api/v1/health）
api_router.include_router(health.router, tags=["健康检查"])

# 认证（/api/v1/auth/...）
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户（/api/v1/users/...）
api_router.include_router(users.router, tags=["用户"])

# 插件（/api/v1/plugins/...）
api_router.include_router(plugins.router, tags=["插件"])

# 分类与标签（/api/v1/categories、/api/v1/tags/popular）
api_router.include_router(categories.router, tags=["分类与标签"])

# 订单（/api/v1/orders/...）
api_router.include_router(orders.router, tags=["订单"])

# 支付（/api/v1/orders/{id}/pay/alipay、/api/v1/payments/alipay/notify）
api_router.include_router(payments.router, tags=["支付"])

# 钱包（/api/v1/wallet/...，仅开发者）
api_router.include_router(wallet.router, tags=["钱包"])

# 评价（/api/v1/plugins/{id}/reviews/...）
api_router.include_router(reviews.router, tags=["评价"])

# 管理后台（/api/v1/admin/...，仅管理员）
api_router.include_router(admin.router, tags=["管理后台"])
