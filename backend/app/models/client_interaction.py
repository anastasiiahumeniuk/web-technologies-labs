from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.database.sessions import BaseModel


class ClientInteraction(BaseModel):
    __tablename__ = "client_interaction"

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("client.id"), primary_key=True, index=True)
    film_id: Mapped[int] = mapped_column(Integer, ForeignKey("film.id"), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, CheckConstraint("score >= 1 AND score <= 10"), nullable=False)
    is_liked: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    client = relationship("Client", back_populates="client_interactions")
    film = relationship("Film", back_populates="client_interactions")
