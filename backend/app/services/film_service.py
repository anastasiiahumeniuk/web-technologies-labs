from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.models import Film

def get_unpopular_movies(db: Session, limit: int = 12):

    stmt = (
        select(Film)
        .where(Film.imdb_rating > 2.0)
        .order_by(Film.imdb_rating)
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()

def get_top_movies_current_year(db: Session, limit: int = 12):

    stmt = (
        select(Film)
        .where(
            Film.year == datetime.now().year,
            Film.imdb_rating >= 8.0
        )
    .order_by(desc(Film.imdb_rating))
    .limit(limit)
    )

    return db.execute(stmt).scalars().all()