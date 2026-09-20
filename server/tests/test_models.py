from sqlalchemy import UniqueConstraint


def test_users_roles_metadata_has_expected_tables_and_constraints():
    from server.app.core.database.base import Base
    from server.app.modules.roles.model import Role
    from server.app.modules.users.model import User, user_roles

    assert User.__tablename__ == "users"
    assert Role.__tablename__ == "roles"
    assert user_roles.name == "user_roles"
    assert {column.name for column in user_roles.primary_key.columns} == {"user_id", "role_id"}

    user_constraints = {constraint.name for constraint in User.__table__.constraints if isinstance(constraint, UniqueConstraint)}
    role_constraints = {constraint.name for constraint in Role.__table__.constraints if isinstance(constraint, UniqueConstraint)}
    assert {"uq_users_username", "uq_users_email"} <= user_constraints
    assert "uq_roles_name" in role_constraints
    assert {"users", "roles", "user_roles"} <= set(Base.metadata.tables)


def test_user_role_relationships_and_defaults_are_declared():
    from server.app.modules.roles.model import Role
    from server.app.modules.users.model import User

    assert "roles" in User.__mapper__.relationships
    assert "users" in Role.__mapper__.relationships
    assert User.__table__.c.is_active.default.arg is True
    assert User.__table__.c.created_at.type.timezone is True
    assert Role.__table__.c.created_at.type.timezone is True
