"""add task delivery fields

Revision ID: 0005_add_task_delivery
Revises: 0004_create_tasks
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_add_task_delivery"
down_revision = "0004_create_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("broker_job_id", sa.String(length=190), nullable=True))
    op.add_column("tasks", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "published_at")
    op.drop_column("tasks", "broker_job_id")
