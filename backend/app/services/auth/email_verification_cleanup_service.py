from datetime import datetime
from sqlalchemy.orm import Session
from app.models.email_verification import EmailVerification

class EmailVerificationCleanupService:
    def __init__(self, db: Session):
        self.db = db

    def cleanup_expired_tokens(self) -> int:
        now = datetime.utcnow()
        deleted = (
            self.db.query(EmailVerification)
            .filter(EmailVerification.expires_at < now, EmailVerification.used == False)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted
