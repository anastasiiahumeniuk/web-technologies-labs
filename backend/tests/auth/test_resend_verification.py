# tests/test_resend_verification.py
from datetime import date, datetime, timedelta
from app.services.auth.resend_verification_service import ResendVerificationService
from app.models.client import Client
from app.models.email_verification import EmailVerification

def test_resend_verification_creates_new_token(db_session):
    client = Client(
        user_name="carol_test",
        email="carol@example.com",
        password_hash="hashed",
        is_active=True,
        confirmed_email=False,
        date_of_birth=date(1990, 1, 1)
    )
    db_session.add(client)
    db_session.commit()

    service = ResendVerificationService(db_session)
    service.resend(client.email)

    verifications = db_session.query(EmailVerification).filter_by(client_id=client.id).all()
    assert len(verifications) == 1
    assert not verifications[0].used