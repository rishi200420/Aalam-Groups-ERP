"""Regression test for the full Alembic migration chain.

The unit tests elsewhere in this suite build their schema with
`Base.metadata.create_all()`, which uses the *current* SQLAlchemy models and
therefore can never catch a broken migration file (a migration that raises,
that assumes a table already exists, or whose DDL/seed data doesn't actually
work on SQLite). This test instead runs `alembic upgrade head` against a
brand new, empty SQLite database -- the same path a fresh install or a
forgotten-to-migrate deployment goes through -- and asserts it succeeds and
produces a schema the app can actually use.
"""

import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = {
    "users", "roles", "permissions", "role_permissions", "user_roles", "refresh_tokens",
    "outlets", "outlet_contacts", "outlet_photos", "outlet_visits",
    "categories", "products", "product_images",
    "orders", "order_items", "order_status_history",
    "dispatches", "dispatch_items", "dispatch_timelines",
    "warehouses", "inventories", "stock_movements",
    "notifications", "system_settings", "notification_preferences",
}


def _fresh_db_url(tmp_path) -> str:
    db_file = tmp_path / "migration_chain_test.db"
    return f"sqlite:///{db_file}"


def _run_upgrade_head(database_url: str) -> None:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def test_migration_chain_runs_cleanly_from_an_empty_database(tmp_path):
    database_url = _fresh_db_url(tmp_path)

    _run_upgrade_head(database_url)

    engine = create_engine(database_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    missing = EXPECTED_TABLES - tables
    assert not missing, f"Migration chain did not create expected tables: {missing}"
    assert "alembic_version" in tables


def test_migration_chain_is_idempotent_when_rerun(tmp_path):
    """Running upgrade head twice (e.g. app restarted twice) must not error."""
    database_url = _fresh_db_url(tmp_path)

    _run_upgrade_head(database_url)
    _run_upgrade_head(database_url)  # should be a no-op, not raise

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "notifications" in inspector.get_table_names()


def test_fresh_schema_accepts_timestamped_inserts(tmp_path):
    """Guards against server_default timestamp expressions that don't
    actually work on SQLite (e.g. raw Postgres-only `now()`), which would
    only surface at INSERT time, not at CREATE TABLE time."""
    database_url = _fresh_db_url(tmp_path)
    _run_upgrade_head(database_url)

    engine = create_engine(database_url)
    with engine.begin() as conn:
        role_id = uuid.uuid4().hex
        conn.execute(
            text("INSERT INTO roles (id, code, name) VALUES (:id, :code, :name)"),
            {"id": role_id, "code": "founder", "name": "Founder"},
        )
        row = conn.execute(text("SELECT created_at, updated_at FROM roles WHERE id = :id"), {"id": role_id}).fetchone()
        assert row is not None
        assert row[0] is not None
        assert row[1] is not None


def test_system_settings_and_notifications_tables_are_usable(tmp_path):
    """Regression guard for the specific bug reported in production: Settings
    and Notifications returned 500s because their migrations existed on disk
    but were never actually applied to the running database."""
    database_url = _fresh_db_url(tmp_path)
    _run_upgrade_head(database_url)

    engine = create_engine(database_url)
    with engine.begin() as conn:
        # system_settings starts empty; the app's own get-or-create logic
        # populates it on first request rather than via a migration-time seed
        # row (a hardcoded id format previously made that seeded row
        # unreachable through the ORM's UUID column type).
        count = conn.execute(text("SELECT COUNT(*) FROM system_settings")).scalar()
        assert count == 0

        user_id = uuid.uuid4().hex
        conn.execute(
            text(
                "INSERT INTO users (id, email, password_hash, full_name, is_active) "
                "VALUES (:id, :email, 'x', 'Test User', 1)"
            ),
            {"id": user_id, "email": "test@example.com"},
        )
        notification_id = uuid.uuid4().hex
        conn.execute(
            text(
                "INSERT INTO notifications (id, user_id, type, title, message, is_read) "
                "VALUES (:id, :user_id, 'system', 'Hello', 'World', 0)"
            ),
            {"id": notification_id, "user_id": user_id},
        )
        row = conn.execute(text("SELECT title FROM notifications WHERE id = :id"), {"id": notification_id}).fetchone()
        assert row is not None
        assert row[0] == "Hello"
