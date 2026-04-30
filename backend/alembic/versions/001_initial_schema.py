"""初始数据库 Schema：创建全部 14 张业务表

Revision ID: 001
Revises:
Create Date: 2026-03-11

表创建顺序严格按外键依赖排列：
1. users（无外键依赖）
2. user_profiles（依赖 users）
3. plugin_categories（自引用，稍后添加父分类约束）
4. plugin_tags（无外键依赖）
5. plugins（依赖 users、plugin_categories；current_version_id 的 FK 延后添加）
6. plugin_tag_relations（依赖 plugins、plugin_tags）
7. plugin_versions（依赖 plugins；创建后再添加 plugins.current_version_id FK）
8. orders（依赖 users、plugins、plugin_versions）
9. transactions（依赖 orders、users）
10. settlements（依赖 users）
11. downloads（依赖 users、plugins、plugin_versions、orders）
12. admin_logs（依赖 users）
13. plugin_reviews（依赖 plugins、users、orders）
14. user_purchases（依赖 users、plugins、orders）
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers，被 alembic 框架读取
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── 启用 PostgreSQL 扩展 ────────────────────────────────────────────────
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # =========================================================================
    # 1. users
    # =========================================================================
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(50), nullable=False),
        sa.Column("avatar_url", sa.String(512), server_default=""),
        sa.Column("role", sa.String(20), nullable=False, server_default="buyer"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_developer", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_login_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_login_ip", postgresql.INET(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint("email_hash", name="uq_users_email_hash"),
        comment="用户核心表，单账号支持买家和开发者双身份",
    )
    op.create_index("idx_users_email_hash", "users", ["email_hash"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_users_status", "users", ["status"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_users_role", "users", ["role"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_users_created_at", "users",
                    [sa.text("created_at DESC")],
                    postgresql_where=sa.text("deleted_at IS NULL"))

    # =========================================================================
    # 2. user_profiles
    # =========================================================================
    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("real_name", sa.String(100), server_default=""),
        sa.Column("phone", sa.String(255), server_default=""),
        sa.Column("phone_hash", sa.String(64), server_default=""),
        sa.Column("bio", sa.Text(), server_default=""),
        sa.Column("website", sa.String(512), server_default=""),
        sa.Column("github_url", sa.String(512), server_default=""),
        sa.Column("company", sa.String(200), server_default=""),
        sa.Column("bank_account", sa.String(255), server_default=""),
        sa.Column("bank_name", sa.String(100), server_default=""),
        sa.Column("alipay_account", sa.String(255), server_default=""),
        sa.Column("wechat_pay_account", sa.String(255), server_default=""),
        sa.Column("total_plugins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_sales", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_revenue", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("avg_rating", sa.Numeric(3, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        comment="用户扩展信息表，包含开发者资料和财务信息",
    )
    op.create_index("idx_user_profiles_user_id", "user_profiles", ["user_id"])
    op.create_index("idx_user_profiles_phone_hash", "user_profiles", ["phone_hash"],
                    postgresql_where=sa.text("phone_hash != ''"))

    # =========================================================================
    # 3. plugin_categories（先不含 parent_id FK，避免自引用鸡-蛋问题）
    # =========================================================================
    op.create_table(
        "plugin_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(255), server_default=""),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("plugin_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.UniqueConstraint("slug", name="uq_plugin_categories_slug"),
        comment="插件分类表，支持树形多级分类",
    )
    # 自引用 FK（表已存在，可以安全添加）
    op.create_foreign_key(
        "fk_plugin_categories_parent_id",
        "plugin_categories", "plugin_categories",
        ["parent_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_plugin_categories_parent_id", "plugin_categories", ["parent_id"])
    op.create_index("idx_plugin_categories_slug", "plugin_categories", ["slug"])
    op.create_index("idx_plugin_categories_sort_order", "plugin_categories", ["sort_order"],
                    postgresql_where=sa.text("is_active = TRUE"))

    # =========================================================================
    # 4. plugin_tags
    # =========================================================================
    op.create_table(
        "plugin_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("plugin_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.UniqueConstraint("name", name="uq_plugin_tags_name"),
        sa.UniqueConstraint("slug", name="uq_plugin_tags_slug"),
        comment="插件标签表，扁平结构",
    )
    op.create_index("idx_plugin_tags_slug", "plugin_tags", ["slug"])

    # =========================================================================
    # 5. plugins（current_version_id FK 先省略，版本表创建后再添加）
    # =========================================================================
    op.create_table(
        "plugins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("developer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("icon_url", sa.String(512), server_default=""),
        sa.Column("screenshots", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="CNY"),
        sa.Column("is_free", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("review_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("review_note", sa.Text(), server_default=""),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("purchase_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_rating", sa.Numeric(3, 2), nullable=False, server_default="0.00"),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_version", sa.String(50), server_default=""),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["developer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["plugin_categories.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("slug", name="uq_plugins_slug"),
        comment="插件主表，存储插件元信息",
    )
    op.create_index("idx_plugins_developer_id", "plugins", ["developer_id"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_plugins_category_id", "plugins", ["category_id"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_plugins_status", "plugins", ["status"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_plugins_slug", "plugins", ["slug"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_plugins_download_count", "plugins",
                    [sa.text("download_count DESC")],
                    postgresql_where=sa.text("deleted_at IS NULL AND status = 'published'"))
    op.create_index("idx_plugins_avg_rating", "plugins",
                    [sa.text("avg_rating DESC")],
                    postgresql_where=sa.text("deleted_at IS NULL AND status = 'published'"))
    op.create_index("idx_plugins_published_at", "plugins",
                    [sa.text("published_at DESC")],
                    postgresql_where=sa.text("deleted_at IS NULL AND status = 'published'"))
    op.create_index("idx_plugins_search", "plugins", ["search_vector"],
                    postgresql_using="gin")

    # =========================================================================
    # 6. plugin_tag_relations
    # =========================================================================
    op.create_table(
        "plugin_tag_relations",
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["plugin_tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("plugin_id", "tag_id"),
        comment="插件与标签的多对多关联表",
    )
    op.create_index("idx_plugin_tag_relations_tag_id", "plugin_tag_relations", ["tag_id"])

    # =========================================================================
    # 7. plugin_versions
    # =========================================================================
    op.create_table(
        "plugin_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=False, server_default=""),
        sa.Column("file_url", sa.String(512), nullable=False),
        sa.Column("file_hash_sha256", sa.String(64), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("min_claw_version", sa.String(50), server_default=""),
        sa.Column("max_claw_version", sa.String(50), server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("review_note", sa.Text(), server_default=""),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("plugin_id", "version", name="uq_plugin_version"),
        comment="插件版本管理表，每次更新插件创建新版本记录",
    )
    op.create_index("idx_plugin_versions_plugin_id", "plugin_versions", ["plugin_id"])
    op.create_index("idx_plugin_versions_status", "plugin_versions", ["status"])
    op.create_index("idx_plugin_versions_published_at", "plugin_versions",
                    [sa.text("published_at DESC")])

    # 现在版本表已建，添加 plugins.current_version_id 的 FK
    op.create_foreign_key(
        "fk_plugins_current_version_id",
        "plugins", "plugin_versions",
        ["current_version_id"], ["id"],
        ondelete="SET NULL",
        use_alter=True,
    )

    # =========================================================================
    # 8. orders
    # =========================================================================
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("order_no", sa.String(32), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plugin_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("developer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="CNY"),
        sa.Column("platform_fee", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("developer_revenue", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("fee_rate", sa.Numeric(5, 4), nullable=False, server_default="0.3000"),
        sa.Column("payment_method", sa.String(20), nullable=False, server_default=""),
        sa.Column("payment_channel", sa.String(50), server_default=""),
        sa.Column("third_party_tx_id", sa.String(128), server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("plugin_snapshot", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["buyer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plugin_version_id"], ["plugin_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["developer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("order_no", name="uq_orders_order_no"),
        comment="订单表，记录每笔购买交易",
    )
    op.create_index("idx_orders_order_no", "orders", ["order_no"])
    op.create_index("idx_orders_buyer_id", "orders", ["buyer_id"])
    op.create_index("idx_orders_developer_id", "orders", ["developer_id"])
    op.create_index("idx_orders_plugin_id", "orders", ["plugin_id"])
    op.create_index("idx_orders_status", "orders", ["status"])
    op.create_index("idx_orders_paid_at", "orders", [sa.text("paid_at DESC")],
                    postgresql_where=sa.text("status = 'paid'"))
    op.create_index("idx_orders_created_at", "orders", [sa.text("created_at DESC")])
    op.create_index("idx_orders_expires_at", "orders", ["expires_at"],
                    postgresql_where=sa.text("status = 'pending'"))
    # 防止同一用户重复购买同一插件（已支付状态的部分唯一索引）
    op.execute(
        "CREATE UNIQUE INDEX uq_orders_buyer_plugin_paid "
        "ON orders (buyer_id, plugin_id) WHERE status = 'paid'"
    )

    # =========================================================================
    # 9. transactions
    # =========================================================================
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tx_no", sa.String(32), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_before", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("balance_after", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="CNY"),
        sa.Column("payment_method", sa.String(20), server_default=""),
        sa.Column("third_party_tx_id", sa.String(128), server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("metadata", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tx_no", name="uq_transactions_tx_no"),
        sa.CheckConstraint("amount > 0", name="chk_transactions_amount_positive"),
        sa.CheckConstraint("direction IN ('in', 'out')", name="chk_transactions_direction"),
        comment="交易流水表，只追加不修改，完整记录每笔资金变动",
    )
    op.create_index("idx_transactions_order_id", "transactions", ["order_id"])
    op.create_index("idx_transactions_user_id", "transactions", ["user_id"])
    op.create_index("idx_transactions_type", "transactions", ["type"])
    op.create_index("idx_transactions_status", "transactions", ["status"])
    op.create_index("idx_transactions_created_at", "transactions", [sa.text("created_at DESC")])
    op.create_index("idx_transactions_third_party", "transactions", ["third_party_tx_id"],
                    postgresql_where=sa.text("third_party_tx_id != ''"))

    # =========================================================================
    # 10. settlements
    # =========================================================================
    op.create_table(
        "settlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("settlement_no", sa.String(32), nullable=False),
        sa.Column("developer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_order_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("platform_fee_total", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("developer_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("adjustment_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("final_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("order_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("withdrawal_method", sa.String(20), server_default=""),
        sa.Column("withdrawal_account", sa.String(255), server_default=""),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), server_default=""),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["developer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("settlement_no", name="uq_settlements_settlement_no"),
        sa.UniqueConstraint("developer_id", "period_start", "period_end",
                            name="uq_settlement_developer_period"),
        sa.CheckConstraint("final_amount >= 0", name="chk_settlements_final_amount"),
        comment="结算表，按 7/15 天周期汇总开发者收入并发起提现",
    )
    op.create_index("idx_settlements_developer_id", "settlements", ["developer_id"])
    op.create_index("idx_settlements_status", "settlements", ["status"])
    op.create_index("idx_settlements_period", "settlements", ["period_start", "period_end"])
    op.create_index("idx_settlements_created_at", "settlements", [sa.text("created_at DESC")])

    # =========================================================================
    # 11. downloads
    # =========================================================================
    op.create_table(
        "downloads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plugin_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.String(512), server_default=""),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plugin_version_id"], ["plugin_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        comment="下载记录表，记录每次插件下载行为",
    )
    op.create_index("idx_downloads_user_id", "downloads", ["user_id"])
    op.create_index("idx_downloads_plugin_id", "downloads", ["plugin_id"])
    op.create_index("idx_downloads_plugin_version_id", "downloads", ["plugin_version_id"])
    op.create_index("idx_downloads_created_at", "downloads", [sa.text("created_at DESC")])

    # =========================================================================
    # 12. admin_logs
    # =========================================================================
    op.create_table(
        "admin_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("admin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("detail", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.String(512), server_default=""),
        sa.Column("reason", sa.Text(), server_default=""),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="RESTRICT"),
        comment="管理后台操作审计日志，只追加不修改",
    )
    op.create_index("idx_admin_logs_admin_id", "admin_logs", ["admin_id"])
    op.create_index("idx_admin_logs_action", "admin_logs", ["action"])
    op.create_index("idx_admin_logs_target", "admin_logs", ["target_type", "target_id"])
    op.create_index("idx_admin_logs_created_at", "admin_logs", [sa.text("created_at DESC")])

    # =========================================================================
    # 13. plugin_reviews
    # =========================================================================
    op.create_table(
        "plugin_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(200), server_default=""),
        sa.Column("content", sa.Text(), server_default=""),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("plugin_id", "user_id", name="uq_plugin_review_user"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="chk_review_rating"),
        comment="插件评价表，支持评分和文字评价",
    )
    op.create_index("idx_plugin_reviews_plugin_id", "plugin_reviews", ["plugin_id"],
                    postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_plugin_reviews_user_id", "plugin_reviews", ["user_id"],
                    postgresql_where=sa.text("deleted_at IS NULL"))

    # =========================================================================
    # 14. user_purchases
    # =========================================================================
    op.create_table(
        "user_purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plugin_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchased_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("user_id", "plugin_id", name="uq_user_purchase"),
        comment="用户已购插件速查表，从订单表派生，支持快速鉴权",
    )
    op.create_index("idx_user_purchases_user_id", "user_purchases", ["user_id"])
    op.create_index("idx_user_purchases_plugin_id", "user_purchases", ["plugin_id"])

    # =========================================================================
    # updated_at 自动更新触发器函数 + 触发器绑定
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    for table in [
        "users", "user_profiles", "plugin_categories",
        "plugins", "orders", "settlements", "plugin_reviews",
    ]:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

    # 全文搜索向量自动更新触发器
    op.execute("""
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
    """)
    op.execute("""
        CREATE TRIGGER trg_plugins_search_vector
            BEFORE INSERT OR UPDATE OF name, summary, description
            ON plugins
            FOR EACH ROW
            EXECUTE FUNCTION update_plugin_search_vector();
    """)


def downgrade() -> None:
    """按照依赖顺序反向删除所有对象。"""
    # 先删触发器和函数
    for table in [
        "users", "user_profiles", "plugin_categories",
        "plugins", "orders", "settlements", "plugin_reviews",
    ]:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table}")
    op.execute("DROP TRIGGER IF EXISTS trg_plugins_search_vector ON plugins")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.execute("DROP FUNCTION IF EXISTS update_plugin_search_vector()")

    # 先删 plugins.current_version_id 的延迟 FK
    op.drop_constraint("fk_plugins_current_version_id", "plugins", type_="foreignkey")

    # 按依赖逆序删表
    op.drop_table("user_purchases")
    op.drop_table("plugin_reviews")
    op.drop_table("admin_logs")
    op.drop_table("downloads")
    op.drop_table("settlements")
    op.drop_table("transactions")
    op.drop_table("orders")
    op.drop_table("plugin_versions")
    op.drop_table("plugin_tag_relations")
    op.drop_table("plugins")
    op.drop_table("plugin_tags")
    op.drop_constraint("fk_plugin_categories_parent_id",
                       "plugin_categories", type_="foreignkey")
    op.drop_table("plugin_categories")
    op.drop_table("user_profiles")
    op.drop_table("users")
