from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Float, ForeignKey
from app.database.sessions import BaseModel

if TYPE_CHECKING:
    from app.models.age_certification import AgeCertification
    from app.models.vectors import Vectors
    from app.models.query_film import QueryFilm

class Film(BaseModel):
    __tablename__ = "film"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    tmdb_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    poster_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    title: Mapped[str] = mapped_column(Text, index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overview: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[str | None] = mapped_column(Text)
    people: Mapped[str | None] = mapped_column(Text)
    imdb_rating: Mapped[float | None] = mapped_column(Float)
    meta_score: Mapped[float | None] = mapped_column(Float)

    age_certification_id: Mapped[int | None] = mapped_column(
        ForeignKey("age_certification.id"),
        nullable=True
    )

    age_certification: Mapped[AgeCertification | None] = relationship(
        "AgeCertification",
        back_populates="films"
    )

    vector_data: Mapped[Vectors | None] = relationship(
        "Vectors",
        back_populates="film",
        uselist=False
    )

    query_associations: Mapped[list["QueryFilm"]] = relationship(back_populates="film")
    client_interactions = relationship("ClientInteraction", back_populates="film")
