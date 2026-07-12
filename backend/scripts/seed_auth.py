"""CLI wrapper for seeding auth data."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal
from app.core.init_db import init_database


def main() -> None:
    init_database()
    print("Auth seed data ready.")


if __name__ == "__main__":
    main()
