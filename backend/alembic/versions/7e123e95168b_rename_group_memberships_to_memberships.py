"""Rename group_memberships to memberships

Revision ID: 7e123e95168b
Revises: b6db28bfaa24
Create Date: 2025-09-18 21:15:30.997047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e123e95168b'
down_revision: Union[str, Sequence[str], None] = 'b6db28bfaa24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename table from group_memberships to memberships
    op.rename_table('group_memberships', 'memberships')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename table back from memberships to group_memberships
    op.rename_table('memberships', 'group_memberships')
