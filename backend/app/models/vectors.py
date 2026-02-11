from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from pgvector.sqlalchemy import Vector
from app.database.sessions import BaseModel

if TYPE_CHECKING:
    from app.models.film import Film

class Vectors(BaseModel):
    __tablename__ = "vectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    film_id: Mapped[int] = mapped_column(
        ForeignKey("film.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(768),
        nullable=True
    )

    film: Mapped[Film] = relationship(
        "Film",
        back_populates="vector_data"
    )
