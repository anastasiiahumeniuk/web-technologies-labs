from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.database.sessions import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.query_film import QueryFilm

class UserQuery(BaseModel):
    __tablename__ = "query"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id", ondelete="CASCADE"), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    # Використовуємо строкову назву класу для relationship
    client: Mapped["Client"] = relationship("Client", back_populates="queries")
    film_associations: Mapped[list["QueryFilm"]] = relationship(back_populates="query")
