from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.client_session import ClientSession
from app.schemas.auth.login import LoginRequest, LoginResponse
from app.utils.security import verify_password
from app.utils.jwt import create_jwt
from app.core.settings import JWT_EXPIRES_DELTA
from app.services.auth.session_cleanup_service import SessionCleanupService
from app.services.auth.email_verification_cleanup_service import EmailVerificationCleanupService

class LoginService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, data: LoginRequest) -> LoginResponse:
        # Очищуємо прострочені токени email verification
        EmailVerificationCleanupService(self.db).cleanup_expired_tokens()

        # Очищуємо прострочені сесії
        SessionCleanupService(self.db).cleanup_expired_sessions()

        client: Client | None = self.db.query(Client).filter(Client.email == data.email).first()
        if not client:
            raise ValueError("Invalid email or password")

        # Перевірка, чи email підтверджено
        if not client.confirmed_email:
            raise ValueError("Email not verified. Please confirm your email to login.")

        # Перевірка пароля
        if not verify_password(data.password, client.password_hash):
            client.failed_logins += 1
            self.db.commit()
            raise ValueError("Invalid email or password")

        # Генеруємо JWT
        token = create_jwt(client.id)
        expires_at = datetime.utcnow() + JWT_EXPIRES_DELTA

        # Зберігаємо сесію
        session = ClientSession(
            client_id=client.id,
            session_token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        self.db.add(session)

        client.last_login = datetime.utcnow()
        self.db.commit()

        return LoginResponse(
            session_token=token,
            expires_at=expires_at
        )
