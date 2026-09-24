"""mark protected system roles

Revision ID: 0012_add_system_role_flag
Revises: 0011_create_departments
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_add_system_role_flag"
down_revision = "0011_create_departments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute(sa.text("UPDATE roles SET is_system = TRUE WHERE name = 'administrator'"))


def downgrade() -> None:
    op.drop_column("roles", "is_system")
