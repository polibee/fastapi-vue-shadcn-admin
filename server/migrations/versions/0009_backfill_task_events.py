"""backfill task creation events

Revision ID: 0009_backfill_task_events
Revises: 0008_create_task_events
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_backfill_task_events"
down_revision = "0008_create_task_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO task_events (task_id, event_type, message, status, progress, created_at)
            SELECT tasks.id, 'created', 'Historical task imported', tasks.status, tasks.progress, tasks.created_at
            FROM tasks
            WHERE NOT EXISTS (
                SELECT 1 FROM task_events
                WHERE task_events.task_id = tasks.id
            )
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM task_events WHERE event_type = 'created' AND message = 'Historical task imported'"))
