from datetime import datetime
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.email_verification import EmailVerification
from app.utils.email_token import generate_email_token
from app.core.settings import EMAIL_VERIFICATION_TOKEN_LIFETIME
from app.services.auth.email_service import EmailService



class ResendVerificationService:

    def __init__(self, db: Session):
        self.db = db

    def resend(self, email: str) -> None:
        # перевірка існування користувача
        client = self.db.query(Client).filter(Client.email == email).first()
        if not client:
            raise ValueError("Client not found")

        # якщо email вже підтверджений
        if client.confirmed_email:
            raise ValueError("Email already confirmed")

        # деактивація старих токенів
        (
            self.db.query(EmailVerification)
            .filter(
                EmailVerification.client_id == client.id,
                EmailVerification.used.is_(False)
            )
            .update({"used": True})
        )

        # генерація нового токена
        token = generate_email_token()
        expires_at = datetime.utcnow() + EMAIL_VERIFICATION_TOKEN_LIFETIME

        verification = EmailVerification(
            client_id=client.id,
            token=token,
            expires_at=expires_at,
            used=False,
        )
        self.db.add(verification)
        self.db.commit()

        # надсилання email (stub)
        self._send_email(client.email, token)

    def _send_email(self, email: str, token: str) -> None:
        EmailService.send_email_verification(email, token)

