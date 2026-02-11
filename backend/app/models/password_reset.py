from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.database.sessions import BaseModel


class PasswordReset(BaseModel):
    __tablename__ = "password_resets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id", ondelete="CASCADE"),
        nullable=False
    )

    token: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False
    )

    used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false"
    )

    client = relationship("Client", back_populates="password_resets")
