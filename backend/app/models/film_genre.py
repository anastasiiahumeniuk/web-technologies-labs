from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from app.database.sessions import BaseModel


class FilmGenre(BaseModel):
    __tablename__ = "film_genre"

    film_id: Mapped[int] = mapped_column(ForeignKey("film.id"), primary_key=True, index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"), primary_key=True, index=True)