"""Repair Alembic history for an existing SQLite database.

This script is intentionally non-destructive. It only stamps the database to
the last pre-inventory revision when the version table is missing and the core
application tables already exist.
"""

from pathlib import Path
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings


TARGET_REVISION = "0006_dispatch_management"


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    alembic_ini = backend_root / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.is_sqlite else {})
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "alembic_version" in tables:
        with engine.connect() as connection:
            existing_revisions = [row[0] for row in connection.execute(text("SELECT version_num FROM alembic_version"))]
        if existing_revisions == [TARGET_REVISION]:
            print("Alembic version table already points at the expected revision. No repair needed.")
            return
        if existing_revisions:
            print("Alembic version table exists but is not aligned with the expected revision. Re-stamping.")
        else:
            print("Alembic version table exists but is empty. Stamping expected revision.")
        command.stamp(config, TARGET_REVISION, purge=True)
        print(f"Stamped database to {TARGET_REVISION}.")
        return

    required_tables = {"permissions", "roles", "users", "outlets", "categories", "products", "orders", "dispatches"}
    missing = sorted(required_tables - tables)
    if missing:
        print("Database does not look like the existing managed schema. Missing:", ", ".join(missing))
        print("No stamp applied.")
        return

    command.stamp(config, TARGET_REVISION)
    print(f"Stamped database to {TARGET_REVISION}.")


if __name__ == "__main__":
    main()