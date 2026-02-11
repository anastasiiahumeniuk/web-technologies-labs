import numpy as np
from sqlalchemy import desc, select, func
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.vectors import Vectors
from app.models.genre import Genre
from app.models.age_certification import AgeCertification
from app.models.film_genre import FilmGenre
from app.models.film import Film
from app.schemas.search import ShowSearch
from app.database.sessions import get_db


def search_films(
    query_vector,
    genres_filter: Optional[List[str]] = None,
    age_cert_filter: Optional[str] = None,
    top_k: int = 10,
    db: Session = None
) -> List[ShowSearch]:
    """
    Search films by vector similarity with optional filters.

    Args:
        query_vector: Vector as string, numpy array, or list
        genres_filter: List of genre names to filter by
        age_cert_filter: Age certification to filter by
        top_k: Number of top results to return
        db: Database session (optional, will create new if not provided)

    Returns:
        List of ShowSearch objects with film information and similarity scores
    """
    if db is None:
        db = next(get_db())
        should_close = True
    else:
        should_close = False

    # Convert query_vector to list format
    if isinstance(query_vector, str):
        query_vector = [float(x.strip()) for x in query_vector.split(',')]
    elif isinstance(query_vector, np.ndarray):
        query_vector = query_vector.ravel().tolist()

    if not isinstance(query_vector, list):
        query_vector = list(query_vector)

    similarity_expr = (1 - Vectors.embedding.cosine_distance(query_vector))

    stmt = (
        select(
            Film.id,
            Film.title,
            Film.year,
            Film.overview,
            Film.poster_path,
            AgeCertification.certification.label("age_cert"),
            func.array_agg(Genre.genre_name).label("genres"),
            similarity_expr.label("similarity")
        )
        .join(Vectors, Film.id == Vectors.film_id)
        .outerjoin(FilmGenre, Film.id == FilmGenre.film_id)
        .outerjoin(Genre, FilmGenre.genre_id == Genre.id)
        .outerjoin(AgeCertification, Film.age_certification_id == AgeCertification.id)
        .where(similarity_expr > 0.5)
    )

    if genres_filter:
        genre_subquery = (
            select(FilmGenre.film_id)
            .join(Genre, FilmGenre.genre_id == Genre.id)
            .where(Genre.genre_name.in_(genres_filter))
        )
        stmt = stmt.where(Film.id.in_(genre_subquery))

    if age_cert_filter:
        stmt = stmt.where(AgeCertification.certification == age_cert_filter)

    stmt = (
        stmt.group_by(
            Film.id,
            Film.title,
            Film.year,
            Film.overview,
            Film.poster_path,
            AgeCertification.certification,
            Vectors.embedding
        )
        .order_by(similarity_expr.desc())
        .limit(top_k)
    )

    results = db.execute(stmt).all()

    if should_close:
        db.close()

    return [
        ShowSearch(
            id=r[0],
            title=r[1],
            year=r[2],
            overview=r[3],
            poster_path=r[4],
            age_cert=r[5],
            genres=r[6] if r[6] else [],
            similarity=float(r[7])
        )
        for r in results
    ]