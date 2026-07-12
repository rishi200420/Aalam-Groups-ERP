import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import get_current_user
from app.core.database import Base, get_db
from app.main import app
from app.schemas.auth import UserRead


def _founder() -> UserRead:
    return UserRead(
        id=str(uuid.uuid4()), email="founder@example.com", full_name="Founder",
        roles=["founder"], is_active=True, created_at=None, updated_at=None,
    )


def test_unhandled_error_response_carries_cors_headers():
    """Regression test for the "Network Error" bug: Starlette routes handlers
    registered for the base Exception class into ServerErrorMiddleware, which
    wraps CORSMiddleware from the outside. Without manually attaching CORS
    headers in the handler, every unhandled 500 anywhere in the app would be
    silently discarded by the browser and surfaced as an opaque network
    failure instead of a readable error."""
    # Build a DB engine that is missing the notifications table, to force a
    # genuine unhandled exception (matching the real-world "migration not
    # yet applied" scenario) rather than an HTTPException.
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    tables = [t for t in Base.metadata.sorted_tables if t.name != "notifications"]
    Base.metadata.create_all(bind=engine, tables=tables)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_current_user] = _founder
    app.dependency_overrides[get_db] = override_get_db
    # raise_server_exceptions=False makes TestClient behave like a real
    # deployed server (return the error response) instead of re-raising the
    # exception in-process, which is what actually happens over real HTTP.
    client = TestClient(app, raise_server_exceptions=False)
    try:
        response = client.get(
            "/api/v1/notifications",
            headers={"Origin": "http://localhost:5173"},
        )
        assert response.status_code == 500
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert response.json()["success"] is False
    finally:
        app.dependency_overrides.clear()
