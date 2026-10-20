"""Align database schema with models

Revision ID: aa3d24fede00
Revises: b3f1280cf09e
Create Date: 2026-10-20 09:27:48.851720

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'aa3d24fede00'
down_revision: Union[str, Sequence[str], None] = 'b3f1280cf09e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_todos_id'), 'todos', ['id'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_todos_id'), table_name='todos')