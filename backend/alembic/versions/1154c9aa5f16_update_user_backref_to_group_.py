"""Update user backref to group_memberships for consistency

Revision ID: 1154c9aa5f16
Revises: ada3e804a8d7
Create Date: 2025-09-18 21:29:59.387596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1154c9aa5f16'
down_revision: Union[str, Sequence[str], None] = 'ada3e804a8d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # リレーションシップのbackref名の一貫性修正はデータベーススキーマに影響しないため、
    # 実際のマイグレーション処理は不要です。
    # この変更は両方向の命名を一貫させるためのSQLAlchemyコードレベルでの修正です。
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # ダウングレード時も同様にデータベース操作は不要です。
    pass
