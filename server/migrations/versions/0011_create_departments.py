"""create departments resource

Revision ID: 0011_create_departments
Revises: 0010_add_role_data_scope
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_create_departments"
down_revision = "0010_add_role_data_scope"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code", name="uq_departments_code"),
    )
    op.create_index("ix_departments_name", "departments", ["name"])
    op.create_index("ix_departments_code", "departments", ["code"])

def downgrade() -> None:
    op.drop_index("ix_departments_code", table_name="departments")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_table("departments")
