"""initial migration

Revision ID: 9411351c4284
Revises:
Create Date: 2026-05-18 21:33:16.769729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9411351c4284'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tbl_users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(), unique=True),
        sa.Column('email', sa.String(), unique=True),
        sa.Column('password', sa.String()),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.Date(), nullable=True),
    )
    op.create_table(
        'tbl_tickets',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('tbl_users.id'), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('tbl_users.id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('tbl_tickets')
    op.drop_table('tbl_users')
