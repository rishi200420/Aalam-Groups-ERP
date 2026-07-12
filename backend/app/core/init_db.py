"""Initialize database seed data when the schema is already managed by Alembic."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.logging import logger
from app.core.seed import seed_auth_data

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def run_migrations():
    logger.info("STEP 1 - Running Alembic")

    try:
        config = Config(str(BACKEND_ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        command.upgrade(config, "head")

        logger.info("STEP 2 - Alembic Finished")

    except Exception:
        logger.exception("Alembic migration failed")
        raise


def init_database():
    logger.info("STEP 3 - init_database()")

    inspector = inspect(engine)

    logger.info("STEP 4 - Inspector Created")

    if "alembic_version" not in inspector.get_table_names():
        logger.warning("Missing alembic_version table")
        return

    logger.info("STEP 5 - Opening Session")

    db = SessionLocal()

    try:
        logger.info("STEP 6 - Starting seed")

        seed_auth_data(db)

        logger.info("STEP 7 - Seed Complete")

    finally:
        db.close()

    logger.info("STEP 8 - Finished")