"""Pytest configuration and fixtures for testing."""

import os
import sys
from typing import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set test environment BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars"
os.environ["DEBUG"] = "true"
os.environ["TESTING"] = "true"

from app.models import Base
from app.main import app
from app.dependencies.database import get_db
from app.dependencies.auth import create_access_token


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Enable foreign key support for SQLite (disabled by default)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency BEFORE any routes are loaded
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create and drop database tables for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test function."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user(db: Session) -> Generator:
    """Create a test user in the database."""
    from app.models.user import User
    
    unique_id = uuid4()
    user = User(
        id=unique_id,
        email=f"test-{unique_id}@example.com",
        hashed_password="hashed_password_placeholder"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user


@pytest.fixture
def user_id(test_user) -> str:
    """Return the test user's ID."""
    return str(test_user.id)


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers with a valid JWT token for the test user."""
    token = create_access_token(user_id=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_dapr(monkeypatch):
    """Mock Dapr client for all tests."""
    from unittest.mock import AsyncMock, MagicMock
    
    mock_client = MagicMock()
    mock_client.schedule_reminder = AsyncMock(return_value=True)
    mock_client.cancel_reminder = AsyncMock(return_value=True)
    mock_client.publish_event = AsyncMock(return_value=True)
    
    monkeypatch.setattr("app.services.reminder_service.get_dapr_client", lambda: mock_client)
    return mock_client


@pytest.fixture(autouse=True)
def mock_publisher(monkeypatch):
    """Mock Kafka publisher for all tests."""
    from unittest.mock import AsyncMock, MagicMock
    
    mock_pub = MagicMock()
    mock_pub.publish = AsyncMock(return_value=True)
    
    # We need to patch get_publisher in all services that use it
    monkeypatch.setattr("app.services.reminder_service.get_publisher", AsyncMock(return_value=mock_pub))
    monkeypatch.setattr("app.services.task_service.get_publisher", AsyncMock(return_value=mock_pub))
    
    return mock_pub
