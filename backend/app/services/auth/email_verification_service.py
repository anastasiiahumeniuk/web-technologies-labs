from datetime import datetime
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.email_verification import EmailVerification


class EmailVerificationService:

    def __init__(self, db: Session):
        self.db = db

    def verify_email(self, token: str) -> None:
        verification = (
            self.db.query(EmailVerification)
            .filter(EmailVerification.token == token)
            .first()
        )

        if not verification:
            raise ValueError("Invalid verification token")

        if verification.used:
            raise ValueError("Verification token already used")

        if verification.expires_at < datetime.utcnow():
            raise ValueError("Verification token expired")

        client = (
            self.db.query(Client)
            .filter(Client.id == verification.client_id)
            .first()
        )

        if not client:
            raise ValueError("Client not found")

        # 🔹 Оновлення стану
        verification.used = True
        client.confirmed_email = True
        client.is_active = True

        self.db.commit()
