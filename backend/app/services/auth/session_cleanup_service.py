from datetime import datetime
from sqlalchemy.orm import Session
from app.models.client_session import ClientSession


class SessionCleanupService:
    def __init__(self, db: Session):
        self.db = db

    def cleanup_expired_sessions(self) -> int:
        now = datetime.utcnow()

        deleted = (
            self.db.query(ClientSession)
            .filter(ClientSession.expires_at < now)
            .delete(synchronize_session=False)
        )

        self.db.commit()
        return deleted
