"""Update relationship backref naming consistency

Revision ID: 01e01aac9dad
Revises: 7e123e95168b
Create Date: 2025-09-18 21:27:25.139582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01e01aac9dad'
down_revision: Union[str, Sequence[str], None] = '7e123e95168b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # リレーションシップのbackref名の変更はデータベーススキーマに影響しないため、
    # 実際のマイグレーション処理は不要です。
    # この変更はSQLAlchemyのPythonコードレベルでの命名の統一です。
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # ダウングレード時も同様にデータベース操作は不要です。
    pass
