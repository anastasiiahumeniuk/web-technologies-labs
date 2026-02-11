from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import  ForeignKey, Numeric
from app.database.sessions import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.query import UserQuery
    from app.models.film import Film

class QueryFilm(BaseModel):
    # Table name
    __tablename__ = "query_film"

    # Columns` definition
    query_id: Mapped[int] = mapped_column(ForeignKey('query.id', ondelete="CASCADE"), primary_key=True)
    film_id: Mapped[int] = mapped_column(ForeignKey('film.id', ondelete="CASCADE"), primary_key=True)
    similarity: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)

    # Relationships with other tables
    query: Mapped["UserQuery"] = relationship(back_populates="film_associations")
    film: Mapped["Film"] = relationship(back_populates="query_associations")