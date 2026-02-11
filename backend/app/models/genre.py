from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.database.sessions import BaseModel

class Genre(BaseModel):
    __tablename__ = 'genre'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    genre_name: Mapped[str] = mapped_column(String(100))