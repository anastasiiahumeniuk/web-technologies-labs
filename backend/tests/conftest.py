import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import patch

# fake jwt
os.environ["JWT_SECRET_KEY"] = "testsecret"
os.environ["JWT_ALGORITHM"] = "HS256"

# --- Fake environment variables for testing ---
os.environ["SMTP_HOST"] = "smtp.example.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_EMAIL"] = "test@example.com"
os.environ["SMTP_PASSWORD"] = "supersecret"
os.environ["SMTP_FROM_NAME"] = "TestApp"
os.environ["FRONTEND_BASE_URL"] = "http://localhost:8000"

from app.database.sessions import BaseModel, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.create_function("lower", 1, lambda string: string.lower() if string else string)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

BaseModel.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    BaseModel.metadata.drop_all(bind=engine)
    BaseModel.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_email_service():

    with patch("app.services.auth.email_service.EmailService.send_email") as mock_send_email, \
         patch("app.services.auth.email_service.EmailService.send_password_reset") as mock_send_reset:
        mock_send_email.return_value = None
        mock_send_reset.return_value = None
        yield