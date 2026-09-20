"""add task lifecycle fields

Revision ID: 0006_add_task_lifecycle
Revises: 0005_add_task_delivery
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_add_task_lifecycle"
down_revision = "0005_add_task_delivery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("progress", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("tasks", sa.Column("message", sa.String(length=255), nullable=True))
    op.add_column("tasks", sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("tasks", sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"))


def downgrade() -> None:
    op.drop_column("tasks", "max_attempts")
    op.drop_column("tasks", "attempts")
    op.drop_column("tasks", "message")
    op.drop_column("tasks", "progress")
