from datetime import datetime
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.email_verification import EmailVerification
from app.schemas.auth.register import RegisterRequest, RegisterResponse
from app.utils.email_token import generate_email_token
from app.utils.security import hash_password
from app.core.settings import EMAIL_VERIFICATION_TOKEN_LIFETIME
from app.services.auth.email_service import EmailService


class RegistrationService:

    def __init__(self, db: Session):
        self.db = db

    def register(self, data: RegisterRequest) -> RegisterResponse:
        existing = self.db.query(Client).filter(Client.email == data.email).first()
        if existing:
            raise ValueError("Email already registered")

        client = Client(
            user_name=data.user_name,
            email=data.email,
            password_hash=hash_password(data.password),
            date_of_birth=data.date_of_birth,
            is_active=False,
            confirmed_email=False,
            failed_logins=0,
        )

        self.db.add(client)
        self.db.flush()

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

        self._send_verification_email(client.email, token)

        # Тут конвертуємо Client у RegisterResponse
        return RegisterResponse(
            id=client.id,
            email=client.email,
            user_name=client.user_name,
            date_of_birth=client.date_of_birth,
            message="User registered successfully. Please check your email to confirm."
        )

    def _send_verification_email(self, email: str, token: str) -> None:
        EmailService.send_email_verification(email, token)

