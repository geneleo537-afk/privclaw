-- ============================================================================
-- 龙虾超市（OpenClaw 插件交易平台）数据库架构
-- 数据库：PostgreSQL 16
-- 字符集：UTF-8
-- 创建日期：2026-03-10
-- ============================================================================

-- 启用必要扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID 生成
CREATE EXTENSION IF NOT EXISTS "pgcrypto";        -- 加密函数
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- 模糊搜索（三元组索引）

-- ============================================================================
-- 1. 用户表 (users)
-- 核心用户账号，单账号双身份（买家 + 开发者）
-- ============================================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL,                          -- 登录邮箱，pgcrypto 加密存储
    email_hash      VARCHAR(64) NOT NULL UNIQUE,                    -- 邮箱 SHA-256 哈希，用于唯一约束和查询
    password_hash   VARCHAR(255) NOT NULL,                          -- bcrypt/argon2id 哈希密码
    nickname        VARCHAR(50) NOT NULL,                           -- 昵称
    avatar_url      VARCHAR(512) DEFAULT '',                        -- 头像 URL
    role            VARCHAR(20) NOT NULL DEFAULT 'buyer',           -- 角色：buyer（纯买家）, developer（已激活开发者身份）
    status          VARCHAR(20) NOT NULL DEFAULT 'active',          -- 状态：active, suspended, banned
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,                 -- 邮箱是否已验证
    is_developer    BOOLEAN NOT NULL DEFAULT FALSE,                 -- 是否已激活开发者身份
    last_login_at   TIMESTAMPTZ,                                    -- 最后登录时间
    last_login_ip   INET,                                           -- 最后登录 IP
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ                                     -- 软删除标记，NULL 表示未删除
);

COMMENT ON TABLE users IS '用户核心表，单账号支持买家和开发者双身份';
COMMENT ON COLUMN users.email IS '登录邮箱，使用 pgcrypto 对称加密存储，密钥由应用层管理';
COMMENT ON COLUMN users.email_hash IS '邮箱 SHA-256 哈希值，用于唯一性校验和登录查询，避免解密';
COMMENT ON COLUMN users.role IS '用户角色：buyer=纯买家, developer=已激活开发者身份';
COMMENT ON COLUMN users.deleted_at IS '软删除时间戳，非 NULL 表示已删除';

-- 用户表索引
CREATE INDEX idx_users_email_hash ON users (email_hash) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status ON users (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role ON users (role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users (created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_nickname_trgm ON users USING gin (nickname gin_trgm_ops) WHERE deleted_at IS NULL;


-- ============================================================================
-- 2. 用户扩展信息表 (user_profiles)
-- 开发者补充信息、财务信息
-- ============================================================================
CREATE TABLE user_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    real_name           VARCHAR(100) DEFAULT '',                     -- 真实姓名（加密存储）
    phone               VARCHAR(255) DEFAULT '',                     -- 手机号（加密存储）
    phone_hash          VARCHAR(64) DEFAULT '',                      -- 手机号哈希，用于查询
    bio                 TEXT DEFAULT '',                              -- 个人简介 / 开发者介绍
    website             VARCHAR(512) DEFAULT '',                     -- 个人网站
    github_url          VARCHAR(512) DEFAULT '',                     -- GitHub 主页
    company             VARCHAR(200) DEFAULT '',                     -- 所属公司/组织

    -- 开发者财务信息（敏感字段加密存储）
    bank_account        VARCHAR(255) DEFAULT '',                     -- 银行账号（加密）
    bank_name           VARCHAR(100) DEFAULT '',                     -- 开户行
    alipay_account      VARCHAR(255) DEFAULT '',                     -- 支付宝账号（加密）
    wechat_pay_account  VARCHAR(255) DEFAULT '',                     -- 微信支付账号（加密）

    -- 开发者统计（非规范化冗余，定期从源表同步）
    total_plugins       INT NOT NULL DEFAULT 0,                      -- 发布插件总数
    total_sales         INT NOT NULL DEFAULT 0,                      -- 总销售量
    total_revenue       NUMERIC(12,2) NOT NULL DEFAULT 0.00,         -- 总收入（开发者分成部分）
    avg_rating          NUMERIC(3,2) NOT NULL DEFAULT 0.00,          -- 平均评分

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE user_profiles IS '用户扩展信息表，包含开发者资料和财务信息';
COMMENT ON COLUMN user_profiles.real_name IS '真实姓名，AES-256-GCM 加密存储';
COMMENT ON COLUMN user_profiles.phone IS '手机号，AES-256-GCM 加密存储';
COMMENT ON COLUMN user_profiles.bank_account IS '银行账号，AES-256-GCM 加密存储';

-- 用户扩展信息索引
CREATE INDEX idx_user_profiles_user_id ON user_profiles (user_id);
CREATE INDEX idx_user_profiles_phone_hash ON user_profiles (phone_hash) WHERE phone_hash != '';


-- ============================================================================
-- 3. 插件分类表 (plugin_categories)
-- 树形分类结构，支持多级分类
-- ============================================================================
CREATE TABLE plugin_categories (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id       UUID REFERENCES plugin_categories(id) ON DELETE SET NULL,   -- 父分类，NULL=顶级分类
    name            VARCHAR(100) NOT NULL,                          -- 分类名称
    slug            VARCHAR(100) NOT NULL UNIQUE,                   -- URL 友好标识
    icon            VARCHAR(255) DEFAULT '',                        -- 分类图标
    description     TEXT DEFAULT '',                                -- 分类描述
    sort_order      INT NOT NULL DEFAULT 0,                         -- 排序权重，值越小越靠前
    plugin_count    INT NOT NULL DEFAULT 0,                         -- 分类下插件数（冗余计数）
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,                  -- 是否启用
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE plugin_categories IS '插件分类表，支持树形多级分类';
COMMENT ON COLUMN plugin_categories.slug IS 'URL 友好标识，全局唯一，如 ai-tools, data-analysis';
COMMENT ON COLUMN plugin_categories.plugin_count IS '冗余计数，由触发器或定时任务维护';

-- 分类表索引
CREATE INDEX idx_plugin_categories_parent_id ON plugin_categories (parent_id);
CREATE INDEX idx_plugin_categories_slug ON plugin_categories (slug);
CREATE INDEX idx_plugin_categories_sort_order ON plugin_categories (sort_order) WHERE is_active = TRUE;


-- ============================================================================
-- 4. 标签表 (plugin_tags)
-- ============================================================================
CREATE TABLE plugin_tags (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(50) NOT NULL UNIQUE,                    -- 标签名
    slug            VARCHAR(50) NOT NULL UNIQUE,                    -- URL 友好标识
    plugin_count    INT NOT NULL DEFAULT 0,                         -- 使用该标签的插件数（冗余）
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE plugin_tags IS '插件标签表，扁平结构';

-- 标签表索引
CREATE INDEX idx_plugin_tags_slug ON plugin_tags (slug);
CREATE INDEX idx_plugin_tags_name_trgm ON plugin_tags USING gin (name gin_trgm_ops);


-- ============================================================================
-- 5. 插件表 (plugins)
-- ============================================================================
CREATE TABLE plugins (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    developer_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,      -- 开发者（不级联删除，防止误删）
    category_id         UUID REFERENCES plugin_categories(id) ON DELETE SET NULL,    -- 所属分类
    name                VARCHAR(200) NOT NULL,                      -- 插件显示名称
    slug                VARCHAR(200) NOT NULL UNIQUE,               -- URL 友好标识，自动添加 clawstore- 前缀
    summary             VARCHAR(500) NOT NULL DEFAULT '',           -- 一句话简介
    description         TEXT NOT NULL DEFAULT '',                   -- 详细描述（Markdown）
    icon_url            VARCHAR(512) DEFAULT '',                    -- 插件图标
    screenshots         JSONB NOT NULL DEFAULT '[]'::jsonb,         -- 截图 URL 数组
    price               NUMERIC(10,2) NOT NULL DEFAULT 0.00,        -- 价格，0=免费
    currency            VARCHAR(3) NOT NULL DEFAULT 'CNY',          -- 货币代码
    is_free             BOOLEAN NOT NULL DEFAULT TRUE,              -- 是否免费
    status              VARCHAR(20) NOT NULL DEFAULT 'draft',       -- 状态：draft, pending_review, published, suspended, removed
    review_status       VARCHAR(20) NOT NULL DEFAULT 'pending',     -- 审核状态：pending, approved, rejected
    review_note         TEXT DEFAULT '',                             -- 审核备注

    -- 统计冗余字段
    download_count      INT NOT NULL DEFAULT 0,                     -- 总下载量
    purchase_count      INT NOT NULL DEFAULT 0,                     -- 总购买量
    avg_rating          NUMERIC(3,2) NOT NULL DEFAULT 0.00,         -- 平均评分
    rating_count        INT NOT NULL DEFAULT 0,                     -- 评分人数

    -- 当前版本快照（冗余，加速列表查询）
    current_version     VARCHAR(50) DEFAULT '',                     -- 当前最新版本号
    current_version_id  UUID,                                       -- 当前最新版本 ID

    -- SEO / 搜索
    search_vector       TSVECTOR,                                   -- 全文搜索向量

    published_at        TIMESTAMPTZ,                                -- 首次发布时间
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ                                 -- 软删除
);

COMMENT ON TABLE plugins IS '插件主表，存储插件元信息';
COMMENT ON COLUMN plugins.slug IS '自动添加 clawstore- 前缀的 URL 标识';
COMMENT ON COLUMN plugins.screenshots IS 'JSONB 数组，存储截图 URL 列表';
COMMENT ON COLUMN plugins.status IS 'draft=草稿, pending_review=待审核, published=已发布, suspended=已下架, removed=已移除';
COMMENT ON COLUMN plugins.search_vector IS '全文搜索向量，由触发器自动维护，覆盖 name + summary + description';

-- 插件表索引
CREATE INDEX idx_plugins_developer_id ON plugins (developer_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugins_category_id ON plugins (category_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugins_status ON plugins (status) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugins_price ON plugins (price) WHERE deleted_at IS NULL AND status = 'published';
CREATE INDEX idx_plugins_download_count ON plugins (download_count DESC) WHERE deleted_at IS NULL AND status = 'published';
CREATE INDEX idx_plugins_purchase_count ON plugins (purchase_count DESC) WHERE deleted_at IS NULL AND status = 'published';
CREATE INDEX idx_plugins_avg_rating ON plugins (avg_rating DESC) WHERE deleted_at IS NULL AND status = 'published';
CREATE INDEX idx_plugins_published_at ON plugins (published_at DESC) WHERE deleted_at IS NULL AND status = 'published';
CREATE INDEX idx_plugins_created_at ON plugins (created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugins_slug ON plugins (slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugins_search ON plugins USING gin (search_vector);
CREATE INDEX idx_plugins_name_trgm ON plugins USING gin (name gin_trgm_ops) WHERE deleted_at IS NULL;

-- 全文搜索向量自动更新触发器
CREATE OR REPLACE FUNCTION update_plugin_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('simple', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_plugins_search_vector
    BEFORE INSERT OR UPDATE OF name, summary, description
    ON plugins
    FOR EACH ROW
    EXECUTE FUNCTION update_plugin_search_vector();


-- ============================================================================
-- 6. 插件-标签关联表 (plugin_tag_relations)
-- ============================================================================
CREATE TABLE plugin_tag_relations (
    plugin_id       UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES plugin_tags(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (plugin_id, tag_id)
);

COMMENT ON TABLE plugin_tag_relations IS '插件与标签的多对多关联表';

-- 关联表索引（反向查询）
CREATE INDEX idx_plugin_tag_relations_tag_id ON plugin_tag_relations (tag_id);


-- ============================================================================
-- 7. 插件版本表 (plugin_versions)
-- ============================================================================
CREATE TABLE plugin_versions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_id           UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    version             VARCHAR(50) NOT NULL,                       -- 语义化版本号（如 1.0.0）
    changelog           TEXT NOT NULL DEFAULT '',                   -- 变更日志（Markdown）
    file_url            VARCHAR(512) NOT NULL,                      -- .md 文件包的对象存储地址
    file_hash_sha256    VARCHAR(64) NOT NULL,                       -- 文件 SHA-256 校验值
    file_size_bytes     BIGINT NOT NULL DEFAULT 0,                  -- 文件大小（字节）
    min_claw_version    VARCHAR(50) DEFAULT '',                     -- 最低兼容 OpenClaw 版本
    max_claw_version    VARCHAR(50) DEFAULT '',                     -- 最高兼容 OpenClaw 版本
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',     -- pending, approved, rejected, yanked
    review_note         TEXT DEFAULT '',                             -- 审核备注
    download_count      INT NOT NULL DEFAULT 0,                     -- 该版本下载量
    published_at        TIMESTAMPTZ,                                -- 该版本发布时间
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 同一插件内版本号唯一
    CONSTRAINT uq_plugin_version UNIQUE (plugin_id, version)
);

COMMENT ON TABLE plugin_versions IS '插件版本管理表，每次更新插件创建新版本记录';
COMMENT ON COLUMN plugin_versions.version IS '语义化版本号，同一 plugin_id 下唯一';
COMMENT ON COLUMN plugin_versions.file_hash_sha256 IS '文件完整性校验，用于下载验证';
COMMENT ON COLUMN plugin_versions.status IS 'pending=待审, approved=通过, rejected=拒绝, yanked=撤回';

-- 版本表索引
CREATE INDEX idx_plugin_versions_plugin_id ON plugin_versions (plugin_id);
CREATE INDEX idx_plugin_versions_status ON plugin_versions (status);
CREATE INDEX idx_plugin_versions_published_at ON plugin_versions (published_at DESC);

-- 添加外键：plugins.current_version_id -> plugin_versions.id
ALTER TABLE plugins
    ADD CONSTRAINT fk_plugins_current_version
    FOREIGN KEY (current_version_id) REFERENCES plugin_versions(id) ON DELETE SET NULL;


-- ============================================================================
-- 8. 订单表 (orders)
-- ============================================================================
CREATE TABLE orders (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_no            VARCHAR(32) NOT NULL UNIQUE,                -- 平台订单号（格式：LC + 年月日 + 序列号）
    buyer_id            UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plugin_id           UUID NOT NULL REFERENCES plugins(id) ON DELETE RESTRICT,
    plugin_version_id   UUID REFERENCES plugin_versions(id) ON DELETE SET NULL,
    developer_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,  -- 冗余开发者 ID，加速分账查询

    -- 金额信息
    original_price      NUMERIC(10,2) NOT NULL,                     -- 原价
    paid_amount         NUMERIC(10,2) NOT NULL,                     -- 实付金额
    discount_amount     NUMERIC(10,2) NOT NULL DEFAULT 0.00,        -- 优惠金额
    currency            VARCHAR(3) NOT NULL DEFAULT 'CNY',

    -- 分账信息
    platform_fee        NUMERIC(10,2) NOT NULL DEFAULT 0.00,        -- 平台抽成（30%）
    developer_revenue   NUMERIC(10,2) NOT NULL DEFAULT 0.00,        -- 开发者收入（70%）
    fee_rate            NUMERIC(5,4) NOT NULL DEFAULT 0.3000,       -- 平台费率（保留精度）

    -- 支付信息
    payment_method      VARCHAR(20) NOT NULL DEFAULT '',            -- wechat_pay, alipay
    payment_channel     VARCHAR(50) DEFAULT '',                     -- 支付渠道详细标识
    third_party_tx_id   VARCHAR(128) DEFAULT '',                    -- 第三方支付流水号

    -- 状态机
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',     -- pending, paid, refunding, refunded, cancelled, closed
    paid_at             TIMESTAMPTZ,                                -- 支付时间
    refunded_at         TIMESTAMPTZ,                                -- 退款时间
    cancelled_at        TIMESTAMPTZ,                                -- 取消时间
    expires_at          TIMESTAMPTZ,                                -- 订单过期时间（未支付自动关闭）

    -- 快照（防止插件修改后订单信息丢失）
    plugin_snapshot     JSONB NOT NULL DEFAULT '{}'::jsonb,         -- 下单时插件快照（名称、版本、价格等）

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE orders IS '订单表，记录每笔购买交易';
COMMENT ON COLUMN orders.order_no IS '平台订单号，格式 LC2026031000001，业务层生成保证唯一';
COMMENT ON COLUMN orders.fee_rate IS '平台费率，默认 30%，保留到万分位支持灵活调整';
COMMENT ON COLUMN orders.plugin_snapshot IS '下单时刻的插件快照，包含 name, version, price 等关键字段';
COMMENT ON COLUMN orders.status IS 'pending=待支付, paid=已支付, refunding=退款中, refunded=已退款, cancelled=已取消, closed=已关闭';

-- 订单表索引
CREATE INDEX idx_orders_order_no ON orders (order_no);
CREATE INDEX idx_orders_buyer_id ON orders (buyer_id);
CREATE INDEX idx_orders_developer_id ON orders (developer_id);
CREATE INDEX idx_orders_plugin_id ON orders (plugin_id);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_paid_at ON orders (paid_at DESC) WHERE status = 'paid';
CREATE INDEX idx_orders_created_at ON orders (created_at DESC);
CREATE INDEX idx_orders_expires_at ON orders (expires_at) WHERE status = 'pending';

-- 防止同一用户重复购买同一插件（已支付状态）
CREATE UNIQUE INDEX uq_orders_buyer_plugin_paid
    ON orders (buyer_id, plugin_id)
    WHERE status = 'paid';


-- ============================================================================
-- 9. 交易流水表 (transactions)
-- 每笔资金变动的完整记录，不可修改，只追加
-- ============================================================================
CREATE TABLE transactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tx_no               VARCHAR(32) NOT NULL UNIQUE,                -- 交易流水号
    order_id            UUID REFERENCES orders(id) ON DELETE RESTRICT,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,  -- 关联用户
    type                VARCHAR(30) NOT NULL,                       -- payment, refund, settlement, withdrawal, platform_fee
    direction           VARCHAR(10) NOT NULL,                       -- in（入账）, out（出账）
    amount              NUMERIC(12,2) NOT NULL,                     -- 金额（正数）
    balance_before      NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 变动前余额
    balance_after       NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 变动后余额
    currency            VARCHAR(3) NOT NULL DEFAULT 'CNY',
    payment_method      VARCHAR(20) DEFAULT '',                     -- 支付方式
    third_party_tx_id   VARCHAR(128) DEFAULT '',                    -- 第三方流水号
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',     -- pending, success, failed
    description         TEXT DEFAULT '',                             -- 交易描述
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,         -- 扩展信息
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 金额必须为正数
    CONSTRAINT chk_transactions_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_transactions_direction CHECK (direction IN ('in', 'out'))
);

COMMENT ON TABLE transactions IS '交易流水表，只追加不修改，完整记录每笔资金变动';
COMMENT ON COLUMN transactions.type IS 'payment=支付, refund=退款, settlement=结算, withdrawal=提现, platform_fee=平台费';
COMMENT ON COLUMN transactions.direction IS 'in=入账, out=出账';
COMMENT ON COLUMN transactions.balance_before IS '该用户在此笔交易前的可用余额';

-- 交易流水索引
CREATE INDEX idx_transactions_order_id ON transactions (order_id);
CREATE INDEX idx_transactions_user_id ON transactions (user_id);
CREATE INDEX idx_transactions_type ON transactions (type);
CREATE INDEX idx_transactions_status ON transactions (status);
CREATE INDEX idx_transactions_created_at ON transactions (created_at DESC);
CREATE INDEX idx_transactions_third_party ON transactions (third_party_tx_id) WHERE third_party_tx_id != '';


-- ============================================================================
-- 10. 结算表 (settlements)
-- 开发者提现/结算周期记录
-- ============================================================================
CREATE TABLE settlements (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    settlement_no       VARCHAR(32) NOT NULL UNIQUE,                -- 结算单号
    developer_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    period_start        DATE NOT NULL,                              -- 结算周期起始日
    period_end          DATE NOT NULL,                              -- 结算周期截止日
    total_order_amount  NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 周期内订单总金额
    platform_fee_total  NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 平台抽成总额
    developer_amount    NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 开发者应得金额
    adjustment_amount   NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 调整金额（退款扣减等）
    final_amount        NUMERIC(12,2) NOT NULL DEFAULT 0.00,        -- 最终结算金额
    order_count         INT NOT NULL DEFAULT 0,                     -- 涉及订单数

    -- 结算状态
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',     -- pending, processing, completed, failed, cancelled
    withdrawal_method   VARCHAR(20) DEFAULT '',                     -- 提现方式：bank, alipay, wechat_pay
    withdrawal_account  VARCHAR(255) DEFAULT '',                    -- 提现账号（加密）
    processed_at        TIMESTAMPTZ,                                -- 处理时间
    completed_at        TIMESTAMPTZ,                                -- 到账时间
    failure_reason      TEXT DEFAULT '',                             -- 失败原因

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 同一开发者同一周期不能重复结算
    CONSTRAINT uq_settlement_developer_period UNIQUE (developer_id, period_start, period_end),
    -- 结算金额不能为负
    CONSTRAINT chk_settlements_final_amount CHECK (final_amount >= 0)
);

COMMENT ON TABLE settlements IS '结算表，按 7/15 天周期汇总开发者收入并发起提现';
COMMENT ON COLUMN settlements.status IS 'pending=待处理, processing=处理中, completed=已到账, failed=失败, cancelled=已取消';
COMMENT ON COLUMN settlements.adjustment_amount IS '退款扣减、违规罚款等调整金额，可为负';

-- 结算表索引
CREATE INDEX idx_settlements_developer_id ON settlements (developer_id);
CREATE INDEX idx_settlements_status ON settlements (status);
CREATE INDEX idx_settlements_period ON settlements (period_start, period_end);
CREATE INDEX idx_settlements_created_at ON settlements (created_at DESC);


-- ============================================================================
-- 11. 下载记录表 (downloads)
-- ============================================================================
CREATE TABLE downloads (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plugin_id           UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    plugin_version_id   UUID NOT NULL REFERENCES plugin_versions(id) ON DELETE CASCADE,
    order_id            UUID REFERENCES orders(id) ON DELETE SET NULL,           -- 付费插件关联订单，免费插件为 NULL
    ip_address          INET,                                       -- 下载时 IP
    user_agent          VARCHAR(512) DEFAULT '',                    -- 客户端信息
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE downloads IS '下载记录表，记录每次插件下载行为';

-- 下载记录索引
CREATE INDEX idx_downloads_user_id ON downloads (user_id);
CREATE INDEX idx_downloads_plugin_id ON downloads (plugin_id);
CREATE INDEX idx_downloads_plugin_version_id ON downloads (plugin_version_id);
CREATE INDEX idx_downloads_created_at ON downloads (created_at DESC);

-- 下载量统计优化（按天分区查询）
CREATE INDEX idx_downloads_plugin_daily ON downloads (plugin_id, created_at::date);


-- ============================================================================
-- 12. 管理操作日志表 (admin_logs)
-- 不可修改，审计追踪
-- ============================================================================
CREATE TABLE admin_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id            UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,  -- 操作管理员
    action              VARCHAR(50) NOT NULL,                       -- 操作类型：plugin_suspend, user_ban, order_refund, settlement_approve 等
    target_type         VARCHAR(50) NOT NULL,                       -- 目标实体类型：user, plugin, order, settlement
    target_id           UUID NOT NULL,                              -- 目标实体 ID
    detail              JSONB NOT NULL DEFAULT '{}'::jsonb,         -- 操作详情（变更前后值）
    ip_address          INET,                                       -- 操作者 IP
    user_agent          VARCHAR(512) DEFAULT '',
    reason              TEXT DEFAULT '',                             -- 操作原因
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE admin_logs IS '管理后台操作审计日志，只追加不修改';
COMMENT ON COLUMN admin_logs.detail IS 'JSONB 格式，记录变更前后的字段值对比';

-- 管理日志索引
CREATE INDEX idx_admin_logs_admin_id ON admin_logs (admin_id);
CREATE INDEX idx_admin_logs_action ON admin_logs (action);
CREATE INDEX idx_admin_logs_target ON admin_logs (target_type, target_id);
CREATE INDEX idx_admin_logs_created_at ON admin_logs (created_at DESC);


-- ============================================================================
-- 13. 插件评价表 (plugin_reviews) [补充表]
-- 支持评分系统需要实体表
-- ============================================================================
CREATE TABLE plugin_reviews (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_id           UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id            UUID REFERENCES orders(id) ON DELETE SET NULL,
    rating              SMALLINT NOT NULL,                          -- 评分 1-5
    title               VARCHAR(200) DEFAULT '',                    -- 评价标题
    content             TEXT DEFAULT '',                             -- 评价内容
    is_visible          BOOLEAN NOT NULL DEFAULT TRUE,              -- 是否可见（管理员可隐藏）
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    -- 同一用户对同一插件只能评价一次
    CONSTRAINT uq_plugin_review_user UNIQUE (plugin_id, user_id),
    CONSTRAINT chk_review_rating CHECK (rating >= 1 AND rating <= 5)
);

COMMENT ON TABLE plugin_reviews IS '插件评价表，支持评分和文字评价';

-- 评价表索引
CREATE INDEX idx_plugin_reviews_plugin_id ON plugin_reviews (plugin_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugin_reviews_user_id ON plugin_reviews (user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugin_reviews_rating ON plugin_reviews (rating) WHERE deleted_at IS NULL;
CREATE INDEX idx_plugin_reviews_created_at ON plugin_reviews (created_at DESC) WHERE deleted_at IS NULL;


-- ============================================================================
-- 14. 用户购买记录表 (user_purchases) [补充表]
-- 用户已购插件的快速查询表
-- ============================================================================
CREATE TABLE user_purchases (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plugin_id           UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    order_id            UUID NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    purchased_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_purchase UNIQUE (user_id, plugin_id)
);

COMMENT ON TABLE user_purchases IS '用户已购插件速查表，从订单表派生，支持快速鉴权';

CREATE INDEX idx_user_purchases_user_id ON user_purchases (user_id);
CREATE INDEX idx_user_purchases_plugin_id ON user_purchases (plugin_id);


-- ============================================================================
-- 通用：updated_at 自动更新触发器函数
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有含 updated_at 的表创建触发器
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_plugin_categories_updated_at BEFORE UPDATE ON plugin_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_plugins_updated_at BEFORE UPDATE ON plugins FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_settlements_updated_at BEFORE UPDATE ON settlements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_plugin_reviews_updated_at BEFORE UPDATE ON plugin_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
