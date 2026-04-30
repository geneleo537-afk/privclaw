# 龙虾超市数据库架构设计

数据库：PostgreSQL 16 | 缓存：Redis 7 | ORM：SQLAlchemy 2.0 + Alembic

---

## 一、数据表总览

共 14 张表，按业务域分为 4 组：

| 业务域     | 表名                   | 说明               |
|-----------|------------------------|--------------------|
| 用户域     | `users`               | 用户核心表          |
| 用户域     | `user_profiles`       | 用户扩展/开发者信息  |
| 插件域     | `plugins`             | 插件主表            |
| 插件域     | `plugin_versions`     | 版本管理表          |
| 插件域     | `plugin_categories`   | 分类表（树形）       |
| 插件域     | `plugin_tags`         | 标签表              |
| 插件域     | `plugin_tag_relations` | 插件-标签关联       |
| 插件域     | `plugin_reviews`      | 插件评价表          |
| 交易域     | `orders`              | 订单表              |
| 交易域     | `transactions`        | 交易流水表          |
| 交易域     | `settlements`         | 结算表              |
| 交易域     | `user_purchases`      | 用户已购速查表       |
| 交易域     | `downloads`           | 下载记录表          |
| 管理域     | `admin_logs`          | 管理操作审计日志     |

---

## 二、各表完整字段定义

### 2.1 users（用户核心表）

单账号支持买家和开发者双身份。邮箱加密存储，哈希值用于查询。

| 字段名          | 类型              | 约束                        | 默认值     | 说明                              |
|-----------------|-------------------|----------------------------|-----------|-----------------------------------|
| id              | UUID              | PK                         | uuid_v4   | 主键                              |
| email           | VARCHAR(255)      | NOT NULL                   | -         | 登录邮箱，pgcrypto 对称加密存储     |
| email_hash      | VARCHAR(64)       | NOT NULL, UNIQUE           | -         | 邮箱 SHA-256 哈希，用于查询和唯一约束 |
| password_hash   | VARCHAR(255)      | NOT NULL                   | -         | bcrypt/argon2id 哈希密码           |
| nickname        | VARCHAR(50)       | NOT NULL                   | -         | 昵称                              |
| avatar_url      | VARCHAR(512)      | -                          | ''        | 头像 URL                          |
| role            | VARCHAR(20)       | NOT NULL                   | 'buyer'   | buyer=买家, developer=开发者       |
| status          | VARCHAR(20)       | NOT NULL                   | 'active'  | active/suspended/banned           |
| email_verified  | BOOLEAN           | NOT NULL                   | FALSE     | 邮箱是否验证                       |
| is_developer    | BOOLEAN           | NOT NULL                   | FALSE     | 是否激活开发者身份                  |
| last_login_at   | TIMESTAMPTZ       | NULLABLE                   | NULL      | 最后登录时间                       |
| last_login_ip   | INET              | NULLABLE                   | NULL      | 最后登录 IP                        |
| created_at      | TIMESTAMPTZ       | NOT NULL                   | NOW()     | 创建时间                           |
| updated_at      | TIMESTAMPTZ       | NOT NULL                   | NOW()     | 更新时间（触发器自动维护）           |
| deleted_at      | TIMESTAMPTZ       | NULLABLE                   | NULL      | 软删除标记                         |

### 2.2 user_profiles（用户扩展信息表）

| 字段名              | 类型           | 约束              | 默认值  | 说明                          |
|---------------------|---------------|-------------------|--------|-------------------------------|
| id                  | UUID          | PK                | uuid_v4 | 主键                          |
| user_id             | UUID          | FK→users, UNIQUE  | -       | 关联用户（一对一）              |
| real_name           | VARCHAR(100)  | -                 | ''      | 真实姓名（AES-256-GCM 加密）   |
| phone               | VARCHAR(255)  | -                 | ''      | 手机号（加密存储）              |
| phone_hash          | VARCHAR(64)   | -                 | ''      | 手机号哈希，用于查询            |
| bio                 | TEXT          | -                 | ''      | 个人简介                       |
| website             | VARCHAR(512)  | -                 | ''      | 个人网站                       |
| github_url          | VARCHAR(512)  | -                 | ''      | GitHub 主页                    |
| company             | VARCHAR(200)  | -                 | ''      | 公司/组织                      |
| bank_account        | VARCHAR(255)  | -                 | ''      | 银行账号（加密存储）            |
| bank_name           | VARCHAR(100)  | -                 | ''      | 开户行                         |
| alipay_account      | VARCHAR(255)  | -                 | ''      | 支付宝账号（加密存储）          |
| wechat_pay_account  | VARCHAR(255)  | -                 | ''      | 微信支付账号（加密存储）        |
| total_plugins       | INT           | NOT NULL          | 0       | 发布插件总数（冗余）            |
| total_sales         | INT           | NOT NULL          | 0       | 总销售量（冗余）               |
| total_revenue       | NUMERIC(12,2) | NOT NULL          | 0.00    | 总收入（冗余）                 |
| avg_rating          | NUMERIC(3,2)  | NOT NULL          | 0.00    | 平均评分（冗余）               |
| created_at          | TIMESTAMPTZ   | NOT NULL          | NOW()   | 创建时间                       |
| updated_at          | TIMESTAMPTZ   | NOT NULL          | NOW()   | 更新时间                       |

### 2.3 plugin_categories（插件分类表）

树形结构，parent_id 自引用实现多级分类。

| 字段名        | 类型          | 约束           | 默认值  | 说明                      |
|--------------|--------------|----------------|--------|---------------------------|
| id           | UUID         | PK             | uuid_v4 | 主键                      |
| parent_id    | UUID         | FK→自身, NULL  | NULL    | 父分类 ID，NULL=顶级      |
| name         | VARCHAR(100) | NOT NULL       | -       | 分类名                    |
| slug         | VARCHAR(100) | UNIQUE         | -       | URL 标识                  |
| icon         | VARCHAR(255) | -              | ''      | 分类图标                   |
| description  | TEXT         | -              | ''      | 分类描述                   |
| sort_order   | INT          | NOT NULL       | 0       | 排序权重                   |
| plugin_count | INT          | NOT NULL       | 0       | 分类下插件数（冗余计数）    |
| is_active    | BOOLEAN      | NOT NULL       | TRUE    | 是否启用                   |
| created_at   | TIMESTAMPTZ  | NOT NULL       | NOW()   | 创建时间                   |
| updated_at   | TIMESTAMPTZ  | NOT NULL       | NOW()   | 更新时间                   |

### 2.4 plugin_tags（标签表）

| 字段名        | 类型         | 约束     | 默认值  | 说明           |
|--------------|-------------|----------|--------|----------------|
| id           | UUID        | PK       | uuid_v4 | 主键           |
| name         | VARCHAR(50) | UNIQUE   | -       | 标签名          |
| slug         | VARCHAR(50) | UNIQUE   | -       | URL 标识        |
| plugin_count | INT         | NOT NULL | 0       | 使用该标签的插件数 |
| created_at   | TIMESTAMPTZ | NOT NULL | NOW()   | 创建时间        |

### 2.5 plugin_tag_relations（插件-标签关联表）

| 字段名      | 类型        | 约束                    | 默认值  | 说明     |
|------------|------------|-------------------------|--------|----------|
| plugin_id  | UUID       | PK, FK→plugins, CASCADE | -      | 插件 ID   |
| tag_id     | UUID       | PK, FK→tags, CASCADE    | -      | 标签 ID   |
| created_at | TIMESTAMPTZ | NOT NULL               | NOW()  | 关联时间  |

### 2.6 plugins（插件主表）

| 字段名              | 类型           | 约束           | 默认值    | 说明                                |
|---------------------|---------------|----------------|----------|-------------------------------------|
| id                  | UUID          | PK             | uuid_v4  | 主键                                |
| developer_id        | UUID          | FK→users       | -        | 开发者（RESTRICT 不级联删除）         |
| category_id         | UUID          | FK→categories  | NULL     | 所属分类                             |
| name                | VARCHAR(200)  | NOT NULL       | -        | 插件显示名称                         |
| slug                | VARCHAR(200)  | UNIQUE         | -        | URL 标识，自动 clawstore- 前缀       |
| summary             | VARCHAR(500)  | -              | ''       | 一句话简介                           |
| description         | TEXT          | -              | ''       | 详细描述（Markdown）                 |
| icon_url            | VARCHAR(512)  | -              | ''       | 插件图标                             |
| screenshots         | JSONB         | NOT NULL       | '[]'     | 截图 URL 数组                        |
| price               | NUMERIC(10,2) | NOT NULL       | 0.00     | 价格，0=免费                         |
| currency            | VARCHAR(3)    | NOT NULL       | 'CNY'   | 货币代码                             |
| is_free             | BOOLEAN       | NOT NULL       | TRUE     | 是否免费                             |
| status              | VARCHAR(20)   | NOT NULL       | 'draft'  | draft/pending_review/published/suspended/removed |
| review_status       | VARCHAR(20)   | NOT NULL       | 'pending'| pending/approved/rejected            |
| review_note         | TEXT          | -              | ''       | 审核备注                             |
| download_count      | INT           | NOT NULL       | 0        | 总下载量（冗余）                      |
| purchase_count      | INT           | NOT NULL       | 0        | 总购买量（冗余）                      |
| avg_rating          | NUMERIC(3,2)  | NOT NULL       | 0.00     | 平均评分（冗余）                      |
| rating_count        | INT           | NOT NULL       | 0        | 评分人数（冗余）                      |
| current_version     | VARCHAR(50)   | -              | ''       | 当前最新版本号（冗余快照）             |
| current_version_id  | UUID          | FK→versions    | NULL     | 当前最新版本 ID                       |
| search_vector       | TSVECTOR      | NULLABLE       | NULL     | 全文搜索向量（触发器自动维护）          |
| published_at        | TIMESTAMPTZ   | NULLABLE       | NULL     | 首次发布时间                          |
| created_at          | TIMESTAMPTZ   | NOT NULL       | NOW()    | 创建时间                              |
| updated_at          | TIMESTAMPTZ   | NOT NULL       | NOW()    | 更新时间                              |
| deleted_at          | TIMESTAMPTZ   | NULLABLE       | NULL     | 软删除                                |

### 2.7 plugin_versions（版本管理表）

| 字段名            | 类型          | 约束                           | 默认值    | 说明                    |
|-------------------|--------------|--------------------------------|----------|-------------------------|
| id                | UUID         | PK                             | uuid_v4  | 主键                    |
| plugin_id         | UUID         | FK→plugins, CASCADE            | -        | 所属插件                 |
| version           | VARCHAR(50)  | UNIQUE(plugin_id, version)     | -        | 语义化版本号             |
| changelog         | TEXT         | -                              | ''       | 变更日志（Markdown）     |
| file_url          | VARCHAR(512) | NOT NULL                       | -        | 文件包对象存储地址        |
| file_hash_sha256  | VARCHAR(64)  | NOT NULL                       | -        | SHA-256 校验值           |
| file_size_bytes   | BIGINT       | NOT NULL                       | 0        | 文件大小（字节）          |
| min_claw_version  | VARCHAR(50)  | -                              | ''       | 最低兼容版本             |
| max_claw_version  | VARCHAR(50)  | -                              | ''       | 最高兼容版本             |
| status            | VARCHAR(20)  | NOT NULL                       | 'pending'| pending/approved/rejected/yanked |
| review_note       | TEXT         | -                              | ''       | 审核备注                 |
| download_count    | INT          | NOT NULL                       | 0        | 该版本下载量             |
| published_at      | TIMESTAMPTZ  | NULLABLE                       | NULL     | 发布时间                 |
| created_at        | TIMESTAMPTZ  | NOT NULL                       | NOW()    | 创建时间                 |

### 2.8 orders（订单表）

| 字段名             | 类型           | 约束          | 默认值    | 说明                         |
|--------------------|---------------|---------------|----------|------------------------------|
| id                 | UUID          | PK            | uuid_v4  | 主键                         |
| order_no           | VARCHAR(32)   | UNIQUE        | -        | 平台订单号 LC+日期+序列       |
| buyer_id           | UUID          | FK→users      | -        | 买家                         |
| plugin_id          | UUID          | FK→plugins    | -        | 购买插件                      |
| plugin_version_id  | UUID          | FK→versions   | NULL     | 购买版本                      |
| developer_id       | UUID          | FK→users      | -        | 开发者（冗余加速分账查询）     |
| original_price     | NUMERIC(10,2) | NOT NULL      | -        | 原价                         |
| paid_amount        | NUMERIC(10,2) | NOT NULL      | -        | 实付金额                      |
| discount_amount    | NUMERIC(10,2) | NOT NULL      | 0.00     | 优惠金额                      |
| currency           | VARCHAR(3)    | NOT NULL      | 'CNY'   | 货币                         |
| platform_fee       | NUMERIC(10,2) | NOT NULL      | 0.00     | 平台抽成 30%                  |
| developer_revenue  | NUMERIC(10,2) | NOT NULL      | 0.00     | 开发者收入 70%                |
| fee_rate           | NUMERIC(5,4)  | NOT NULL      | 0.3000   | 平台费率                      |
| payment_method     | VARCHAR(20)   | -             | ''       | wechat_pay/alipay             |
| payment_channel    | VARCHAR(50)   | -             | ''       | 支付渠道详细标识               |
| third_party_tx_id  | VARCHAR(128)  | -             | ''       | 第三方支付流水号               |
| status             | VARCHAR(20)   | NOT NULL      | 'pending'| pending/paid/refunding/refunded/cancelled/closed |
| paid_at            | TIMESTAMPTZ   | NULLABLE      | NULL     | 支付时间                      |
| refunded_at        | TIMESTAMPTZ   | NULLABLE      | NULL     | 退款时间                      |
| cancelled_at       | TIMESTAMPTZ   | NULLABLE      | NULL     | 取消时间                      |
| expires_at         | TIMESTAMPTZ   | NULLABLE      | NULL     | 未支付过期时间                 |
| plugin_snapshot    | JSONB         | NOT NULL      | '{}'     | 下单时插件快照                 |
| created_at         | TIMESTAMPTZ   | NOT NULL      | NOW()    | 创建时间                      |
| updated_at         | TIMESTAMPTZ   | NOT NULL      | NOW()    | 更新时间                      |

### 2.9 transactions（交易流水表）

只追加不修改，完整审计追踪。

| 字段名            | 类型           | 约束                       | 默认值    | 说明                       |
|-------------------|---------------|----------------------------|----------|----------------------------|
| id                | UUID          | PK                         | uuid_v4  | 主键                       |
| tx_no             | VARCHAR(32)   | UNIQUE                     | -        | 交易流水号                  |
| order_id          | UUID          | FK→orders                  | NULL     | 关联订单                    |
| user_id           | UUID          | FK→users                   | -        | 关联用户                    |
| type              | VARCHAR(30)   | NOT NULL                   | -        | payment/refund/settlement/withdrawal/platform_fee |
| direction         | VARCHAR(10)   | NOT NULL, CHECK(in/out)    | -        | in=入账, out=出账           |
| amount            | NUMERIC(12,2) | NOT NULL, CHECK(>0)        | -        | 金额（正数）                |
| balance_before    | NUMERIC(12,2) | NOT NULL                   | 0.00     | 变动前余额                  |
| balance_after     | NUMERIC(12,2) | NOT NULL                   | 0.00     | 变动后余额                  |
| currency          | VARCHAR(3)    | NOT NULL                   | 'CNY'   | 货币                       |
| payment_method    | VARCHAR(20)   | -                          | ''       | 支付方式                    |
| third_party_tx_id | VARCHAR(128)  | -                          | ''       | 第三方流水号                 |
| status            | VARCHAR(20)   | NOT NULL                   | 'pending'| pending/success/failed      |
| description       | TEXT          | -                          | ''       | 交易描述                    |
| metadata          | JSONB         | NOT NULL                   | '{}'     | 扩展信息                    |
| created_at        | TIMESTAMPTZ   | NOT NULL                   | NOW()    | 创建时间                    |

### 2.10 settlements（结算表）

| 字段名              | 类型           | 约束                                    | 默认值    | 说明                    |
|---------------------|---------------|-----------------------------------------|----------|-------------------------|
| id                  | UUID          | PK                                      | uuid_v4  | 主键                    |
| settlement_no       | VARCHAR(32)   | UNIQUE                                  | -        | 结算单号                 |
| developer_id        | UUID          | FK→users                                | -        | 开发者                   |
| period_start        | DATE          | NOT NULL                                | -        | 结算周期起始             |
| period_end          | DATE          | NOT NULL                                | -        | 结算周期截止             |
| total_order_amount  | NUMERIC(12,2) | NOT NULL                                | 0.00     | 周期内订单总额           |
| platform_fee_total  | NUMERIC(12,2) | NOT NULL                                | 0.00     | 平台抽成总额             |
| developer_amount    | NUMERIC(12,2) | NOT NULL                                | 0.00     | 开发者应得金额           |
| adjustment_amount   | NUMERIC(12,2) | NOT NULL                                | 0.00     | 调整金额（退款扣减等）    |
| final_amount        | NUMERIC(12,2) | NOT NULL, CHECK(>=0)                    | 0.00     | 最终结算金额             |
| order_count         | INT           | NOT NULL                                | 0        | 涉及订单数               |
| status              | VARCHAR(20)   | NOT NULL                                | 'pending'| pending/processing/completed/failed/cancelled |
| withdrawal_method   | VARCHAR(20)   | -                                       | ''       | bank/alipay/wechat_pay  |
| withdrawal_account  | VARCHAR(255)  | -                                       | ''       | 提现账号（加密）          |
| processed_at        | TIMESTAMPTZ   | NULLABLE                                | NULL     | 处理时间                 |
| completed_at        | TIMESTAMPTZ   | NULLABLE                                | NULL     | 到账时间                 |
| failure_reason      | TEXT          | -                                       | ''       | 失败原因                 |
| created_at          | TIMESTAMPTZ   | NOT NULL                                | NOW()    | 创建时间                 |
| updated_at          | TIMESTAMPTZ   | NOT NULL                                | NOW()    | 更新时间                 |

**唯一约束**：同一开发者同一周期不可重复结算 `UNIQUE(developer_id, period_start, period_end)`

### 2.11 downloads（下载记录表）

| 字段名            | 类型         | 约束              | 默认值  | 说明               |
|-------------------|-------------|-------------------|--------|--------------------|
| id                | UUID        | PK                | uuid_v4 | 主键              |
| user_id           | UUID        | FK→users          | -       | 下载用户           |
| plugin_id         | UUID        | FK→plugins        | -       | 下载插件           |
| plugin_version_id | UUID        | FK→versions       | -       | 下载版本           |
| order_id          | UUID        | FK→orders, NULL   | NULL    | 关联订单（免费为NULL）|
| ip_address        | INET        | NULLABLE          | NULL    | 下载 IP            |
| user_agent        | VARCHAR(512)| -                 | ''      | 客户端信息          |
| created_at        | TIMESTAMPTZ | NOT NULL          | NOW()   | 下载时间           |

### 2.12 admin_logs（管理操作日志表）

只追加不修改，审计追踪。

| 字段名       | 类型         | 约束      | 默认值  | 说明                     |
|-------------|-------------|-----------|--------|--------------------------|
| id          | UUID        | PK        | uuid_v4 | 主键                    |
| admin_id    | UUID        | FK→users  | -       | 操作管理员               |
| action      | VARCHAR(50) | NOT NULL  | -       | 操作类型                 |
| target_type | VARCHAR(50) | NOT NULL  | -       | 目标实体类型              |
| target_id   | UUID        | NOT NULL  | -       | 目标实体 ID              |
| detail      | JSONB       | NOT NULL  | '{}'    | 变更前后值对比            |
| ip_address  | INET        | NULLABLE  | NULL    | 操作者 IP                |
| user_agent  | VARCHAR(512)| -         | ''      | 客户端信息               |
| reason      | TEXT        | -         | ''      | 操作原因                 |
| created_at  | TIMESTAMPTZ | NOT NULL  | NOW()   | 操作时间                 |

### 2.13 plugin_reviews（插件评价表）

| 字段名     | 类型         | 约束                              | 默认值  | 说明              |
|-----------|-------------|-----------------------------------|--------|-------------------|
| id        | UUID        | PK                                | uuid_v4 | 主键             |
| plugin_id | UUID        | FK→plugins, UNIQUE(plugin+user)   | -       | 评价的插件        |
| user_id   | UUID        | FK→users, UNIQUE(plugin+user)     | -       | 评价用户          |
| order_id  | UUID        | FK→orders, NULL                   | NULL    | 关联订单          |
| rating    | SMALLINT    | NOT NULL, CHECK(1-5)              | -       | 评分 1-5          |
| title     | VARCHAR(200)| -                                 | ''      | 评价标题          |
| content   | TEXT        | -                                 | ''      | 评价内容          |
| is_visible| BOOLEAN     | NOT NULL                          | TRUE    | 是否可见          |
| created_at| TIMESTAMPTZ | NOT NULL                          | NOW()   | 创建时间          |
| updated_at| TIMESTAMPTZ | NOT NULL                          | NOW()   | 更新时间          |
| deleted_at| TIMESTAMPTZ | NULLABLE                          | NULL    | 软删除            |

### 2.14 user_purchases（用户已购速查表）

| 字段名       | 类型        | 约束                           | 默认值  | 说明         |
|-------------|------------|--------------------------------|--------|-------------|
| id          | UUID       | PK                             | uuid_v4 | 主键        |
| user_id     | UUID       | FK→users, UNIQUE(user+plugin)  | -       | 买家        |
| plugin_id   | UUID       | FK→plugins, UNIQUE(user+plugin)| -       | 购买的插件   |
| order_id    | UUID       | FK→orders                      | -       | 关联订单     |
| purchased_at| TIMESTAMPTZ| NOT NULL                       | NOW()   | 购买时间     |

---

## 三、表关系图

```
users 1:1 user_profiles              （一个用户一份扩展信息）

users 1:N plugins                    （一个开发者发布多个插件）
users 1:N orders [buyer_id]          （一个买家产生多个订单）
users 1:N orders [developer_id]      （一个开发者关联多个订单收入）
users 1:N transactions               （一个用户产生多条流水）
users 1:N settlements                （一个开发者多次结算）
users 1:N downloads                  （一个用户多次下载）
users 1:N admin_logs                 （一个管理员多条操作日志）
users 1:N plugin_reviews             （一个用户多条评价）
users 1:N user_purchases             （一个用户多次购买）

plugins N:1 plugin_categories        （多个插件属于同一分类）
plugins 1:N plugin_versions          （一个插件多个版本）
plugins M:N plugin_tags              （通过 plugin_tag_relations 多对多）
plugins 1:N orders                   （一个插件被多次购买）
plugins 1:N downloads                （一个插件被多次下载）
plugins 1:N plugin_reviews           （一个插件多条评价）
plugins 1:N user_purchases           （一个插件被多人购买）

plugin_categories 自引用 N:1         （子分类→父分类，树形结构）

orders 1:N transactions              （一个订单产生多条流水：支付+分账+退款）
orders 1:1 user_purchases            （已支付订单对应一条购买记录）

plugin_versions 1:N downloads        （一个版本被下载多次）
```

**关系可视化**：

```
                    ┌──────────────┐
                    │    users     │
                    └──────┬───────┘
                           │
          ┌────────────────┼──────────────────┐
          │                │                  │
    ┌─────▼─────┐   ┌─────▼──────┐   ┌──────▼────────┐
    │user_profiles│  │  plugins   │   │   orders      │
    └───────────┘   └─────┬──────┘   └──────┬────────┘
                          │                  │
           ┌──────────────┼──────┐    ┌──────┼──────┐
           │              │      │    │      │      │
     ┌─────▼──────┐ ┌────▼───┐  │  ┌─▼──┐ ┌─▼───┐  │
     │plugin_ver- │ │plugin_ │  │  │tx  │ │user_│  │
     │sions       │ │reviews │  │  │    │ │purch│  │
     └─────┬──────┘ └────────┘  │  └────┘ └─────┘  │
           │                    │                   │
     ┌─────▼──────┐      ┌─────▼──────┐     ┌─────▼──────┐
     │ downloads  │      │plugin_tag_ │     │settlements │
     └────────────┘      │relations   │     └────────────┘
                         └─────┬──────┘
                               │
                         ┌─────▼──────┐
                         │plugin_tags │
                         └────────────┘

              ┌──────────────────┐
              │plugin_categories │ ← 自引用树形
              └──────────────────┘

              ┌──────────────────┐
              │   admin_logs     │ ← 独立审计
              └──────────────────┘
```

---

## 四、关键索引设计

### 4.1 索引策略总表

| 表名               | 索引名                              | 字段                        | 类型      | 条件（部分索引）                 | 设计理由                                |
|--------------------|-------------------------------------|-----------------------------|-----------|--------------------------------|----------------------------------------|
| users              | idx_users_email_hash                | email_hash                  | B-tree    | deleted_at IS NULL             | 登录查询核心路径，排除已删除用户          |
| users              | idx_users_status                    | status                      | B-tree    | deleted_at IS NULL             | 管理后台按状态筛选                       |
| users              | idx_users_nickname_trgm             | nickname                    | GIN/trgm  | deleted_at IS NULL             | 用户昵称模糊搜索                         |
| plugins            | idx_plugins_developer_id            | developer_id                | B-tree    | deleted_at IS NULL             | 开发者查看自己的插件列表                  |
| plugins            | idx_plugins_category_id             | category_id                 | B-tree    | deleted_at IS NULL             | 分类页插件列表                           |
| plugins            | idx_plugins_download_count          | download_count DESC         | B-tree    | status='published', !deleted   | 热门排序                                |
| plugins            | idx_plugins_published_at            | published_at DESC           | B-tree    | status='published', !deleted   | 最新排序                                |
| plugins            | idx_plugins_avg_rating              | avg_rating DESC             | B-tree    | status='published', !deleted   | 评分排序                                |
| plugins            | idx_plugins_search                  | search_vector               | GIN       | 无                             | 全文搜索（TSVECTOR）                    |
| plugins            | idx_plugins_name_trgm               | name                        | GIN/trgm  | deleted_at IS NULL             | 插件名模糊搜索                           |
| plugins            | idx_plugins_slug                    | slug                        | B-tree    | deleted_at IS NULL             | 插件详情页 URL 路由                      |
| plugin_versions    | uq_plugin_version                   | (plugin_id, version)        | B-tree    | 无（唯一约束）                  | 同一插件版本号不可重复                    |
| plugin_tag_rels    | idx_plugin_tag_relations_tag_id     | tag_id                      | B-tree    | 无                             | 按标签查插件的反向查询                    |
| orders             | idx_orders_buyer_id                 | buyer_id                    | B-tree    | 无                             | 用户查看自己的订单                       |
| orders             | idx_orders_developer_id             | developer_id                | B-tree    | 无                             | 开发者查看收入订单                       |
| orders             | idx_orders_expires_at               | expires_at                  | B-tree    | status='pending'               | 定时任务关闭过期未支付订单                |
| orders             | uq_orders_buyer_plugin_paid         | (buyer_id, plugin_id)       | B-tree    | status='paid'                  | 防止重复购买                             |
| transactions       | idx_transactions_user_id            | user_id                     | B-tree    | 无                             | 用户流水查询                             |
| transactions       | idx_transactions_third_party        | third_party_tx_id           | B-tree    | third_party_tx_id != ''        | 支付回调对账                             |
| settlements        | idx_settlements_developer_id        | developer_id                | B-tree    | 无                             | 开发者查看结算记录                       |
| downloads          | idx_downloads_plugin_daily          | (plugin_id, created_at::date)| B-tree   | 无                             | 按日统计下载量                           |
| admin_logs         | idx_admin_logs_target               | (target_type, target_id)    | B-tree    | 无                             | 查看某实体的所有管理操作                  |

### 4.2 索引设计原则

1. **部分索引（Partial Index）优先**：大量使用 `WHERE deleted_at IS NULL` 和 `WHERE status = 'published'` 过滤条件，减小索引体积，提升查询效率
2. **GIN + pg_trgm 支撑模糊搜索**：用户搜索插件名、昵称时，三元组索引支持 `LIKE '%关键词%'` 而不会全表扫描
3. **TSVECTOR 全文搜索**：插件的 name/summary/description 三个字段按权重（A/B/C）合并到 search_vector，支持 `ts_query` 搜索
4. **冗余字段替代 JOIN**：download_count、purchase_count 等冗余在 plugins 表内，列表排序查询无需 JOIN，显著降低查询复杂度

---

## 五、Redis 缓存策略

### 5.1 缓存架构

```
Redis 7 集群
├── 热点数据缓存
├── 会话管理
├── 分布式锁
├── 计数器
└── 消息队列（BullMQ/Celery broker）
```

### 5.2 缓存数据详细设计

| 缓存 Key 模式                          | 数据内容                | TTL      | 更新策略                      | 说明                          |
|----------------------------------------|------------------------|----------|-------------------------------|-------------------------------|
| `session:{session_id}`                 | 用户会话信息            | 24h      | 登录时写入，登出时删除          | JWT + Redis 双重验证           |
| `user:{user_id}`                       | 用户基础信息            | 30min    | Cache-Aside，写时失效          | 昵称、头像、角色等高频读字段    |
| `plugin:{plugin_id}`                   | 插件详情               | 15min    | Cache-Aside，写时失效          | 详情页渲染数据                 |
| `plugin:slug:{slug}`                   | plugin_id 映射         | 1h       | 写时失效                       | URL slug 到 ID 的快速映射      |
| `plugin:list:cat:{cat_id}:sort:{type}:p:{page}` | 分类+排序的分页列表 | 5min  | 有新插件发布或排序变化时失效     | 商城列表页核心缓存             |
| `plugin:list:hot:p:{page}`             | 热门插件分页            | 5min     | 定时任务刷新                   | 首页热门推荐                   |
| `plugin:list:new:p:{page}`             | 最新插件分页            | 3min     | 有新插件发布时失效              | 首页最新发布                   |
| `search:{query_hash}:p:{page}`         | 搜索结果缓存            | 2min     | 短 TTL 自然过期                | 搜索结果，短缓存避免数据陈旧    |
| `category:tree`                        | 完整分类树              | 1h       | 分类变更时失效                  | 导航栏/侧边栏分类展示          |
| `tag:popular`                          | 热门标签列表            | 30min    | 标签计数变化时失效              | 标签云展示                     |
| `counter:plugin:{id}:downloads`        | 下载计数器              | 持久     | INCR 原子递增，定期写回 DB      | 高并发下载计数，避免频繁 UPDATE |
| `counter:plugin:{id}:views`            | 浏览计数器              | 持久     | INCR 原子递增，定期写回 DB      | 浏览量统计                     |
| `rate_limit:api:{user_id}`             | API 限流计数器          | 1min     | 滑动窗口计数                   | 接口限流保护                   |
| `rate_limit:download:{user_id}`        | 下载限流                | 1h       | 滑动窗口计数                   | 防止批量下载                   |
| `lock:order:{order_no}`                | 分布式锁               | 30s      | 获取锁时设置，完成后释放        | 支付回调幂等处理               |
| `lock:settlement:{settlement_no}`      | 结算锁                 | 60s      | 获取锁时设置，完成后释放        | 结算任务防重                   |
| `user:{user_id}:purchases`             | 用户已购插件 ID 集合    | 30min    | Cache-Aside                   | 插件列表页快速标记"已购买"      |
| `email_verify:{token}`                 | 邮箱验证令牌            | 24h      | 创建时写入，使用后删除          | 注册邮箱验证                   |
| `password_reset:{token}`               | 密码重置令牌            | 1h       | 创建时写入，使用后删除          | 找回密码                       |

### 5.3 缓存更新策略

**主策略：Cache-Aside（旁路缓存）**

```
读取路径：
1. 先查 Redis
2. 命中 → 直接返回
3. 未命中 → 查 PostgreSQL → 写入 Redis（设置 TTL）→ 返回

写入路径：
1. 更新 PostgreSQL
2. 删除对应 Redis 缓存键（而非更新，避免并发不一致）
3. 下次读取自动回源
```

**计数器策略：Write-Behind（写回）**

```
高频计数（下载量、浏览量）：
1. 直接 INCR Redis 计数器
2. 定时任务（每 5 分钟）批量写回 PostgreSQL
3. 单次写回使用事务：UPDATE plugins SET download_count = download_count + delta
```

**缓存击穿防护**：

```
1. 热点 Key 使用互斥锁（SETNX）防止缓存击穿
2. 空值缓存：查询无结果时缓存空标记，TTL=60s，防止穿透
3. 随机 TTL 抖动：TTL = base_ttl + random(0, 60s)，防止雪崩
```

---

## 六、数据安全方案

### 6.1 敏感字段加密方案

| 字段               | 所在表           | 加密方式              | 查询方案                      |
|--------------------|-----------------|----------------------|-------------------------------|
| email              | users           | AES-256-GCM 对称加密  | 通过 email_hash (SHA-256) 查询 |
| phone              | user_profiles   | AES-256-GCM 对称加密  | 通过 phone_hash (SHA-256) 查询 |
| real_name          | user_profiles   | AES-256-GCM 对称加密  | 不支持搜索，仅详情页解密展示    |
| bank_account       | user_profiles   | AES-256-GCM 对称加密  | 不支持搜索，仅结算时解密使用    |
| alipay_account     | user_profiles   | AES-256-GCM 对称加密  | 不支持搜索，仅结算时解密使用    |
| wechat_pay_account | user_profiles   | AES-256-GCM 对称加密  | 不支持搜索，仅结算时解密使用    |
| withdrawal_account | settlements     | AES-256-GCM 对称加密  | 不支持搜索，仅结算处理时解密    |
| password_hash      | users           | Argon2id 单向哈希     | 验证时重新哈希对比             |

**加密实施细节**：

```
加密密钥管理：
├── 主密钥存储在环境变量 / KMS 服务，绝不写入代码或数据库
├── 每个字段使用独立的数据加密密钥（DEK），DEK 由主密钥（KEK）加密存储
├── 密钥轮转周期：90 天
└── 加密在应用层（Python）执行，数据库存储密文

加密格式：
{version}:{nonce_base64}:{ciphertext_base64}:{tag_base64}
版本号便于后续密钥轮转时区分新旧密文

哈希方案：
├── 邮箱/手机号哈希：SHA-256(salt + lowercase(value))
├── 盐值从主密钥派生，固定不变（确保相同输入产生相同哈希）
└── 密码哈希：Argon2id(password, random_salt) — 每个用户独立随机盐
```

### 6.2 软删除策略

**适用软删除的表**（有 `deleted_at` 字段）：

| 表名            | 理由                                        |
|-----------------|---------------------------------------------|
| users           | 用户注销后保留数据 30 天，支持后悔恢复；关联订单/流水需要追溯 |
| plugins         | 下架插件保留记录，已购用户仍可查看历史订单关联信息 |
| plugin_reviews  | 评价删除后可能需要审计追溯                     |

**不使用软删除的表**：

| 表名               | 理由                                          |
|--------------------|-----------------------------------------------|
| orders             | 订单不可删除，通过 status 管理生命周期           |
| transactions       | 流水不可删除不可修改，财务审计要求               |
| admin_logs         | 审计日志不可删除不可修改                        |
| settlements        | 结算记录不可删除，通过 status 管理              |
| downloads          | 下载记录不可删除，统计依赖数据完整性             |
| plugin_versions    | 版本不可删除，通过 status=yanked 标记撤回       |
| plugin_categories  | 通过 is_active=FALSE 禁用，不删除               |
| plugin_tags        | 标签不删除，仅解除关联                          |
| user_profiles      | 跟随 users 表 CASCADE 级联                     |
| plugin_tag_relations | 跟随 plugins/tags CASCADE 级联              |
| user_purchases     | 跟随 users/plugins CASCADE 级联               |

**软删除查询约定**：

```sql
-- 所有查询默认过滤已删除记录
SELECT * FROM users WHERE deleted_at IS NULL;

-- 部分索引自动优化
CREATE INDEX idx_xxx ON table (col) WHERE deleted_at IS NULL;

-- 管理后台可查看已删除记录
SELECT * FROM users WHERE deleted_at IS NOT NULL;

-- 物理清理：定时任务清理 deleted_at 超过 90 天的记录
DELETE FROM users WHERE deleted_at < NOW() - INTERVAL '90 days';
```

### 6.3 其他安全措施

**行级安全（RLS）**：

```sql
-- 开发者只能查看自己的插件
ALTER TABLE plugins ENABLE ROW LEVEL SECURITY;
CREATE POLICY developer_plugin_policy ON plugins
    FOR ALL TO app_developer_role
    USING (developer_id = current_setting('app.current_user_id')::uuid);
```

**审计追踪**：
- `admin_logs` 表记录所有管理员操作，包含操作前后数据快照
- `transactions` 表记录所有资金变动，只追加不修改
- 关键操作（封号、下架、退款）强制写入 admin_logs

**SQL 注入防护**：
- 全部使用 SQLAlchemy ORM 参数化查询，禁止字符串拼接 SQL
- 输入校验层（Pydantic）在到达 ORM 前过滤非法输入

**数据备份**：
- PostgreSQL 开启 WAL 归档，支持时间点恢复（PITR）
- 每日全量备份 + 持续 WAL 增量
- 备份数据加密存储，保留周期 30 天

---

## 七、补充设计说明

### 7.1 主键策略

全部使用 UUID v4 作为主键：
- 分布式环境下无需协调即可生成
- 不暴露业务量信息（相比自增 ID）
- 前端可预生成 ID 实现乐观更新

业务编号（order_no、tx_no、settlement_no）使用应用层雪花算法生成，兼具有序性和全局唯一性。

### 7.2 时间字段

- 全部使用 `TIMESTAMPTZ`（带时区），存储 UTC，展示时由应用层转换时区
- `created_at` 使用数据库 `DEFAULT NOW()` 保证精度
- `updated_at` 使用触发器自动维护

### 7.3 金额字段

- 使用 `NUMERIC(10,2)` / `NUMERIC(12,2)`，精确到分
- 禁止使用 FLOAT/DOUBLE 存储金额
- 平台费率 `fee_rate` 使用 `NUMERIC(5,4)` 精确到万分位

### 7.4 状态机设计

**订单状态流转**：

```
pending ──(支付成功)──→ paid
pending ──(超时)──────→ closed
pending ──(用户取消)──→ cancelled
paid ────(申请退款)──→ refunding
refunding (退款成功)──→ refunded
refunding (退款拒绝)──→ paid
```

**插件状态流转**：

```
draft ──(提交审核)──→ pending_review
pending_review ──(审核通过)──→ published
pending_review ──(审核拒绝)──→ draft
published ──(管理员下架)──→ suspended
published ──(开发者下架)──→ removed
suspended ──(恢复上架)──→ published
```

### 7.5 分账计算

```
订单实付金额: paid_amount
平台抽成:    platform_fee    = ROUND(paid_amount * fee_rate, 2)
开发者收入:  developer_revenue = paid_amount - platform_fee

注意：先算平台抽成再做减法，避免浮点精度问题。
fee_rate 默认 0.3000（30%），存储在订单内，支持后续按开发者等级调整费率。
```
