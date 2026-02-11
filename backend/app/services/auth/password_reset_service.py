from datetime import datetime
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.password_reset import PasswordReset
from app.models.client_session import ClientSession
from app.utils.security import hash_password
from app.utils.reset_token import generate_reset_token
from app.core.settings import PASSWORD_RESET_TOKEN_LIFETIME
from app.services.auth.email_service import EmailService


class PasswordResetService:

    def __init__(self, db: Session):
        self.db = db

    # Очищаємо прострочені токени
    def _cleanup_expired_tokens(self) -> int:
        now = datetime.utcnow()
        deleted = (
            self.db.query(PasswordReset)
            .filter(
                PasswordReset.expires_at < now,
                PasswordReset.used.is_(False)
            )
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted

    # Генерація токена (викликається з endpoint /request-password-reset)
    def generate_reset_token(self, email: str) -> str:
        # Видаляємо прострочені токени
        self._cleanup_expired_tokens()

        client = (
            self.db.query(Client)
            .filter(Client.email == email)
            .first()
        )

        # Нічого не розкриваємо назовні
        if not client:
            return ""

        # Блокуємо генерацію токена, якщо email не підтверджено
        if not client.confirmed_email:
            raise ValueError("Email not verified. Cannot reset password.")

        # деактивуємо старі токени
        self.db.query(PasswordReset)\
            .filter(
                PasswordReset.client_id == client.id,
                PasswordReset.used.is_(False)
            )\
            .update({"used": True})

        token = generate_reset_token()
        expires_at = datetime.utcnow() + PASSWORD_RESET_TOKEN_LIFETIME

        reset = PasswordReset(
            client_id=client.id,
            token=token,
            expires_at=expires_at,
            used=False,
        )

        self.db.add(reset)
        self.db.commit()

        self._send_reset_email(client.email, token)

        return token

    # Валідація токена (внутрішній метод)
    def _validate_token(self, token: str) -> PasswordReset:
        reset = (
            self.db.query(PasswordReset)
            .filter(PasswordReset.token == token)
            .first()
        )

        if not reset:
            raise ValueError("Invalid reset token")

        if reset.used:
            raise ValueError("Reset token already used")

        if reset.expires_at < datetime.utcnow():
            raise ValueError("Reset token expired")

        return reset

    # Скидання пароля (викликається з /reset-password)
    def reset_password(self, token: str, new_password: str) -> datetime:
        reset = self._validate_token(token)

        client = (
            self.db.query(Client)
            .filter(Client.id == reset.client_id)
            .first()
        )

        if not client:
            raise ValueError("Client not found")

        client.password_hash = hash_password(new_password)
        client.updated_at = datetime.utcnow()

        # одноразовий токен
        reset.used = True

        # інвалід усіх сесій
        self.db.query(ClientSession)\
            .filter(ClientSession.client_id == client.id)\
            .delete()

        self.db.commit()

        return client.updated_at

    def _send_reset_email(self, email: str, token: str) -> None:
        EmailService.send_password_reset(email, token)

