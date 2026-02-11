# tests/test_password_reset.py
import pytest
from datetime import datetime, timedelta, date

from app.services.auth.password_reset_service import PasswordResetService
from app.models.client import Client
from app.models.password_reset import PasswordReset
from app.models.client_session import ClientSession
from app.utils.security import hash_password


@pytest.fixture
def client(db_session):
    user = Client(
        user_name="test_user",
        email="test@example.com",
        password_hash=hash_password("OldPassword123"),
        date_of_birth=date(1990, 1, 1),
        is_active=True,
        confirmed_email=True,
        failed_logins=0,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def service(db_session):
    return PasswordResetService(db_session)


def test_generate_reset_token_creates_token(service, client, db_session):
    token = service.generate_reset_token(client.email)
    assert token != ""
    reset_record = db_session.query(PasswordReset).filter_by(client_id=client.id).first()
    assert reset_record is not None
    assert reset_record.token == token
    assert reset_record.used is False
    assert reset_record.expires_at > datetime.utcnow()


def test_generate_reset_token_nonexistent_email(service, db_session):
    token = service.generate_reset_token("nonexistent@example.com")
    assert token == ""


def test_reset_password_updates_password_and_invalidates_sessions(service, client, db_session):
    old_hash = client.password_hash

    token = service.generate_reset_token(client.email)

    session = ClientSession(
        client_id=client.id,
        session_token="fake-session",
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db_session.add(session)
    db_session.commit()

    updated_at = service.reset_password(token, "NewPassword123")

    updated_client = db_session.query(Client).filter_by(id=client.id).first()
    assert updated_client.password_hash != old_hash

    reset_record = db_session.query(PasswordReset).filter_by(token=token).first()
    assert reset_record.used is True

    sessions = db_session.query(ClientSession).filter_by(client_id=client.id).all()
    assert len(sessions) == 0

    assert isinstance(updated_at, datetime)


def test_reset_password_expired_token(service, client, db_session):
    token = service.generate_reset_token(client.email)
    reset_record = db_session.query(PasswordReset).filter_by(token=token).first()
    reset_record.expires_at = datetime.utcnow() - timedelta(seconds=1)
    db_session.commit()

    with pytest.raises(ValueError, match="Reset token expired"):
        service.reset_password(token, "NewPassword123")


def test_reset_password_used_token(service, client, db_session):
    token = service.generate_reset_token(client.email)
    reset_record = db_session.query(PasswordReset).filter_by(token=token).first()
    reset_record.used = True
    db_session.commit()

    with pytest.raises(ValueError, match="Reset token already used"):
        service.reset_password(token, "NewPassword123")