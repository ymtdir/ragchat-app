"""Add partial unique constraints for soft delete

Revision ID: a9e515ec096c
Revises: 4db9b4227c31
Create Date: 2025-09-17 19:23:06.920854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9e515ec096c'
down_revision: Union[str, Sequence[str], None] = '4db9b4227c31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 既存のUNIQUE制約を削除（存在する場合のみ）
    op.execute("DROP INDEX IF EXISTS ix_users_name")
    op.execute("DROP INDEX IF EXISTS ix_users_email")
    
    # 論理削除を考慮した部分UNIQUE制約を追加
    # アクティブなユーザーのみでユニーク制約を適用
    op.execute("""
        CREATE UNIQUE INDEX ix_users_name_unique_active 
        ON users (name) 
        WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE UNIQUE INDEX ix_users_email_unique_active 
        ON users (email) 
        WHERE deleted_at IS NULL
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # 部分UNIQUE制約を削除
    op.execute("DROP INDEX IF EXISTS ix_users_email_unique_active")
    op.execute("DROP INDEX IF EXISTS ix_users_name_unique_active")
    
    # 元のUNIQUE制約を復元
    op.create_unique_constraint('ix_users_email', 'users', ['email'])
    op.create_unique_constraint('ix_users_name', 'users', ['name'])
