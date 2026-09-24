"""add the protected detailed health permission

Revision ID: 0013_add_health_detail_permission
Revises: 0012_add_system_role_flag
"""
from alembic import op
import sqlalchemy as sa


revision = "0013_add_health_detail_permission"
down_revision = "0012_add_system_role_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO permissions (code, description)
            SELECT 'health.detail', 'View detailed application health'
            WHERE NOT EXISTS (
                SELECT 1 FROM permissions WHERE code = 'health.detail'
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT roles.id, permissions.id
            FROM roles
            CROSS JOIN permissions
            WHERE roles.name = 'administrator'
              AND permissions.code = 'health.detail'
              AND NOT EXISTS (
                  SELECT 1
                  FROM role_permissions existing
                  WHERE existing.role_id = roles.id
                    AND existing.permission_id = permissions.id
              )
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (
                SELECT id FROM permissions WHERE code = 'health.detail'
            )
            """
        )
    )
    op.execute(sa.text("DELETE FROM permissions WHERE code = 'health.detail'"))
