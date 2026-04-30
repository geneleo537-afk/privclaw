"""修复 settlements 表唯一约束：移除 uq_settlement_developer_period

Revision ID: 002
Revises: 001
Create Date: 2026-03-11

问题说明：
  001 迁移在 settlements 表上建了 UNIQUE(developer_id, period_start, period_end)。
  该约束原为"按周期汇总结算"设计，但实际业务中 settlements 表被用作"按需提现申请"，
  开发者可在同一自然月内多次申请提现（前一笔审批完成后再发起下一笔）。

  当开发者在 3 月申请第一笔提现（period_start=3月1日, period_end=3月31日）并通过后，
  再申请第二笔时 period_start/period_end 完全相同 → DB 抛出唯一约束冲突。

修复方案：
  删除该联合唯一索引，允许同一开发者在相同周期内创建多条结算记录。
  wallet.py 路由已通过业务层检查（status IN pending/processing）防止并发重复申请。
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """删除导致多次提现冲突的联合唯一约束。"""
    op.drop_constraint(
        "uq_settlement_developer_period",
        "settlements",
        type_="unique",
    )


def downgrade() -> None:
    """恢复原有联合唯一约束（会导致数据冲突，仅用于测试回滚）。"""
    op.create_unique_constraint(
        "uq_settlement_developer_period",
        "settlements",
        ["developer_id", "period_start", "period_end"],
    )
