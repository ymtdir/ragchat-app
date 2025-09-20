"""Add group_memberships table

Revision ID: b6db28bfaa24
Revises: f44efe8b8507
Create Date: 2025-09-18 21:08:44.067626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6db28bfaa24'
down_revision: Union[str, Sequence[str], None] = 'f44efe8b8507'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create group_memberships table
    op.create_table(
        'group_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'group_id', 'deleted_at', name='unique_active_membership')
    )

    # Create indexes
    op.create_index(op.f('ix_group_memberships_id'), 'group_memberships', ['id'], unique=False)
    op.create_index(op.f('ix_group_memberships_user_id'), 'group_memberships', ['user_id'], unique=False)
    op.create_index(op.f('ix_group_memberships_group_id'), 'group_memberships', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_memberships_deleted_at'), 'group_memberships', ['deleted_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_group_memberships_deleted_at'), table_name='group_memberships')
    op.drop_index(op.f('ix_group_memberships_group_id'), table_name='group_memberships')
    op.drop_index(op.f('ix_group_memberships_user_id'), table_name='group_memberships')
    op.drop_index(op.f('ix_group_memberships_id'), table_name='group_memberships')

    # Drop table
    op.drop_table('group_memberships')
