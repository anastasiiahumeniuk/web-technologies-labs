# tests/test_email_verification.py
import pytest
from datetime import date, datetime, timedelta
from app.services.auth.email_verification_service import EmailVerificationService
from app.models.client import Client
from app.models.email_verification import EmailVerification

def test_verify_email_success(db_session):
    client = Client(
        user_name="bob_test",
        email="bob@example.com",
        password_hash="hashed",
        is_active=True,
        confirmed_email=False,
        date_of_birth=date(1990, 1, 1)
    )
    db_session.add(client)
    db_session.commit()

    verification = EmailVerification(
        client_id=client.id,
        token="token123",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        used=False
    )
    db_session.add(verification)
    db_session.commit()

    service = EmailVerificationService(db_session)
    service.verify_email("token123")

    db_session.refresh(verification)
    db_session.refresh(client)

    assert verification.used
    assert client.confirmed_email