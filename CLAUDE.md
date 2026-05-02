# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PrivClaw - A secure, enterprise-oriented AI plugin marketplace serving OpenClaw workflow customization.

## Tech Stack

- **Backend**: FastAPI 0.115.6 + Python 3.12 + SQLAlchemy 2.0 async + asyncpg + PostgreSQL 16
- **Frontend**: Next.js 15.1.3 + React 19 + TypeScript 5 + TailwindCSS 4
- **Cache/Queue**: Redis 7 (Celery broker)
- **Async Tasks**: Celery 5.4.0
- **Object Storage**: MinIO (dev) / Aliyun OSS (production)
- **Payment**: Alipay SDK (sandbox & production)
- **State Management**: Zustand (auth persistence) + React Query (API caching)
- **UI**: Radix UI + Lucide React icons + React Hot Toast

## Common Commands

```bash
# Development (Docker Compose)
make dev              # Start all services (postgres, redis, minio, backend, celery, frontend)
make down             # Stop all containers
make logs             # View logs

# Database migrations (Alembic)
make migrate          # Run migrations
make migration msg="description"  # Generate new migration

# Testing
make test             # Run backend pytest
make seed             # Initialize demo data

# Container Shell
make shell-be         # Enter backend container
make shell-fe         # Enter frontend container

# Frontend standalone (in frontend/ directory)
npm run dev           # Dev server (port 3000)
npm run build         # Production build
npm run lint          # ESLint check

# Production deployment
make prod             # Start production (with nginx)
make build            # Build production images
```

## 架构设计

### 后端分层架构 (`1.1/backend/app/`)

```
API 路由层 (api/v1/*.py)
    ↓ FastAPI 依赖注入 (core/deps.py)
服务层 (services/*.py)  ← 核心业务逻辑
    ↓
ORM 模型层 (models/*.py)  ← SQLAlchemy async
    ↓
PostgreSQL + Redis
```

- **路由聚合**: `api/v1/router.py` 统一注册所有子路由（auth, users, plugins, orders, payments, categories, wallet, admin）
- **统一响应格式**: `Response[T]` (code, message, data) 和 `PageResponse[T]`，定义在 `schemas/` 中
- **依赖注入**: `core/deps.py` 提供 `get_db`, `get_current_user` 等 FastAPI 依赖
- **配置管理**: `core/config.py` 使用 Pydantic Settings，环境变量驱动
- **存储适配器模式**: `services/storage/` 中 `BaseStorage` → `MinIOBackend` | `OSSBackend`，通过 `STORAGE_BACKEND` 环境变量切换
- **支付服务**: `services/payment/` 支持支付宝和钱包余额两种支付方式

### 认证安全体系

- JWT 双 Token 机制：Access Token 15 分钟 + Refresh Token 7 天
- Token 轮换：刷新时旧 Refresh Token 作废
- Redis 管理 Token 黑名单/白名单
- 密码哈希：passlib (bcrypt)
- 安全相关代码集中在 `core/security.py`

### 前端架构 (`1.1/frontend/src/`)

- **App Router 分组路由**: `(main)` 主页面、`(auth)` 认证、`(dashboard)` 用户面板、`(admin)` 管理后台
- **API 客户端**: `lib/api-client.ts` — Axios 实例，拦截器自动注入 Token 和 401 自动刷新
- **认证状态**: `stores/auth-store.ts` — Zustand + persist 中间件（localStorage）
- **数据获取**: `hooks/` 目录下封装 React Query hooks（use-auth, use-plugins, use-orders, use-wallet）
- **类型定义**: `types/` 目录集中管理 API 响应类型
- **路径别名**: `@/*` → `./src/*`

### 异步任务 (Celery)

- `tasks/order_timeout.py`: 订单超时自动关闭（30 分钟倒计时）
- Redis 作为 Celery broker (`CELERY_BROKER_URL`)

## 部署架构

- **开发**: `docker-compose.yml` — 6 个服务（postgres, redis, minio, backend, celery-worker, frontend）
- **生产**: `docker-compose.prod.yml` 覆盖配置 — backend 用 gunicorn 4 workers，frontend standalone 模式，新增 nginx 反向代理
- **Nginx** (`deploy/nginx/default.conf`): 限速策略、安全响应头、API 文档仅内网访问、恶意扫描器屏蔽

## 环境变量

- **开发**: `1.1/.env.dev` — 预配置完整，可直接 `make dev` 启动
- **生产**: `1.1/.env.prod.example` — 模板文件，需手动填写真实密钥
- 关键变量: `DATABASE_URL`, `REDIS_URL`, `STORAGE_BACKEND`, `ALIPAY_APP_ID`, `JWT_SECRET_KEY`, `CORS_ORIGINS`

## 数据库迁移

- 使用 Alembic，迁移脚本在 `1.1/backend/alembic/versions/`
- 当前有 2 个迁移版本：初始 schema + 结算唯一约束修复
- 新迁移: `make migration msg="描述"`，执行: `make migrate`

## 开发注意事项

- Next.js 图片远程模式白名单配置在 `next.config.ts`（localhost:9000, 122.51.185.112:9000, *.aliyuncs.com）
- 前端无测试框架，后端使用 pytest + pytest-asyncio + httpx
- 无 pre-commit hooks 配置
- ESLint 继承 `next/core-web-vitals` + `next/typescript`
