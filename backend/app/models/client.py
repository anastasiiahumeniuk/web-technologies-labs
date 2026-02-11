from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Date, Boolean
from sqlalchemy.sql import func
from datetime import datetime, date
from app.database.sessions import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.query import UserQuery
    from app.models.email_verification import EmailVerification
    from app.models.client_session import ClientSession
    from app.models.password_reset import PasswordReset

class Client(BaseModel):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    confirmed_email: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    failed_logins: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    queries = relationship("UserQuery", back_populates="client")
    email_verifications = relationship("EmailVerification", back_populates="client", cascade="all, delete-orphan")
    sessions = relationship("ClientSession", back_populates="client", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="client", cascade="all, delete-orphan")
    client_interactions = relationship("ClientInteraction", back_populates="client")
