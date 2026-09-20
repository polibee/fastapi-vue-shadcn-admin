"""add task recovery fields

Revision ID: 0007_add_task_recovery_fields
Revises: 0006_add_task_lifecycle
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_add_task_recovery_fields"
down_revision = "0006_add_task_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("error_message", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "error_message")
    op.drop_column("tasks", "started_at")
