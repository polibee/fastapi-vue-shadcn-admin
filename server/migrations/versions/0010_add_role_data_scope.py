"""add role data scope

Revision ID: 0010_add_role_data_scope
Revises: 0009_backfill_task_events
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_add_role_data_scope"
down_revision = "0009_backfill_task_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("data_scope", sa.String(length=16), nullable=False, server_default="all"))


def downgrade() -> None:
    op.drop_column("roles", "data_scope")
