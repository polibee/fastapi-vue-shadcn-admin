import importlib


def test_initial_migration_is_reversible_and_owns_core_tables():
    migration = importlib.import_module("server.migrations.versions.0001_create_users_roles")

    assert migration.revision == "0001_create_users_roles"
    assert migration.down_revision is None
    source = migration.upgrade.__code__.co_names
    assert "create_table" in source
    assert "users" in migration.__dict__["TABLE_NAMES"]
    assert "roles" in migration.__dict__["TABLE_NAMES"]
    assert "user_roles" in migration.__dict__["TABLE_NAMES"]
