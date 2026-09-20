"""create task records

Revision ID: 0004_create_tasks
Revises: 0003_create_audit_logs
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_create_tasks"
down_revision = "0003_create_audit_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tasks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("task_id", sa.String(length=64), nullable=False), sa.Column("task_name", sa.String(length=128), nullable=False), sa.Column("status", sa.String(length=32), nullable=False), sa.Column("payload_json", sa.Text(), nullable=False), sa.Column("requested_by", sa.Integer(), nullable=True), sa.Column("request_id", sa.String(length=64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"), sa.UniqueConstraint("task_id"))
    op.create_index("ix_tasks_task_id", "tasks", ["task_id"], unique=False)
    op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("ix_tasks_request_id", "tasks", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tasks_request_id", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_task_id", table_name="tasks")
    op.drop_table("tasks")
