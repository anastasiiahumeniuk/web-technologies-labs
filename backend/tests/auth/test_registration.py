# tests/test_registration.py
from datetime import date, datetime

from app.services.auth.registration_service import RegistrationService
from app.models.client import Client
from app.models.email_verification import EmailVerification
from app.utils.security import verify_password
from app.schemas.auth.register import RegisterRequest


def test_register_creates_client(db_session):
    service = RegistrationService(db_session)

    data = RegisterRequest(
        user_name="john_doe",
        email="john@example.com",
        password="Password123",
        date_of_birth=date(1990, 1, 1)
    )

    response = service.register(data)

    assert response.id is not None
    assert response.email == data.email
    assert response.user_name == data.user_name
    assert response.date_of_birth == data.date_of_birth

    client_in_db = db_session.query(Client).filter_by(id=response.id).first()
    assert client_in_db is not None
    assert client_in_db.email == data.email
    assert client_in_db.user_name == data.user_name
    assert not client_in_db.is_active
    assert not client_in_db.confirmed_email
    assert verify_password(data.password, client_in_db.password_hash)


def test_register_creates_email_verification(db_session):
    service = RegistrationService(db_session)

    data = RegisterRequest(
        user_name="alice_smith",
        email="alice@example.com",
        password="Password123",
        date_of_birth=date(1995, 6, 15)
    )

    client = service.register(data)

    verification = (
        db_session.query(EmailVerification)
        .filter_by(client_id=client.id)
        .first()
    )

    assert verification is not None
    assert not verification.used
    assert verification.expires_at > datetime.utcnow()