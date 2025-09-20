"""Fix relationship backref naming collision

Revision ID: ada3e804a8d7
Revises: 01e01aac9dad
Create Date: 2025-09-18 21:28:57.525778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ada3e804a8d7'
down_revision: Union[str, Sequence[str], None] = '01e01aac9dad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # リレーションシップのbackref名の修正はデータベーススキーマに影響しないため、
    # 実際のマイグレーション処理は不要です。
    # この変更は名前衝突を避けるためのSQLAlchemyコードレベルでの修正です。
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # ダウングレード時も同様にデータベース操作は不要です。
    pass
