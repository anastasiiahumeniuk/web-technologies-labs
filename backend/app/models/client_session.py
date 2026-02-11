from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.sessions import BaseModel
from app.models.client import Client

class ClientSession(BaseModel):
    __tablename__ = "client_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    session_token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    client = relationship("Client", back_populates="sessions")
