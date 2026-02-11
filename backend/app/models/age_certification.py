from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from app.database.sessions import BaseModel

if TYPE_CHECKING:
    from app.models.film import Film

class AgeCertification(BaseModel):
    __tablename__ = "age_certification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    certification: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


    films: Mapped[List[Film]] = relationship(
        "Film",
        back_populates="age_certification"
    )