from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.database.sessions import BaseModel


class Admin(BaseModel):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(
        String,
        nullable=True,
        server_default="admin"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=True
    )
