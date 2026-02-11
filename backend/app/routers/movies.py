from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from typing import List, Optional
import logging
from datetime import datetime
from app.database.sessions import get_db
from app.models.age_certification import AgeCertification
from app.models.film import Film
from app.models.film_genre import FilmGenre
from app.models.genre import Genre
from app.schemas.movies import MovieResponse, MovieDetailResponse, MovieHomeRead
from app.services.film_service import get_unpopular_movies, get_top_movies_current_year

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get("", response_model=List[MovieResponse])
def get_movies_list(
    years: Optional[List[int]] = Query(None),
    end_year: Optional[int] = None,
    genres: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = None,
    age_certification: Optional[str] = None,
    sort_by: str = Query("imdb_rating"),
    order: str = Query("desc"),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    logger.info("Filtering movies: genres=%s, years=%s, sort_by=%s", genres, years, sort_by)

    sort_mapping = {
        "imdb_rating": Film.imdb_rating,
        "year": Film.year,
        "title": Film.title
    }
    sort_column = sort_mapping.get(sort_by, Film.imdb_rating)
    sorting_clause = asc(sort_column) if order == "asc" else desc(sort_column)

    subq = select(Film.id)

    if genres:
        subq = (
            subq
            .join(FilmGenre, FilmGenre.film_id == Film.id)
            .join(Genre, Genre.id == FilmGenre.genre_id)
            .where(Genre.genre_name.in_(genres))
        )

    if years:
        subq = subq.where(Film.year.in_(years))

    if end_year:
        subq = subq.where(Film.year <= end_year)

    if min_rating:
        subq = subq.where(Film.imdb_rating >= min_rating)

    if age_certification:
        subq = (
            subq
            .join(AgeCertification, AgeCertification.id == Film.age_certification_id)
            .where(AgeCertification.certification == age_certification)
        )

    subq = (
        subq
        .order_by(sorting_clause, Film.id)
        .offset(offset)
        .limit(limit)
        .subquery()
    )

    stmt = (
        select(Film)
        .where(Film.id.in_(select(subq.c.id)))
        .order_by(sorting_clause, Film.id)
    )

    return db.execute(stmt).scalars().all()

@router.get("/search", response_model=List[MovieResponse])
def search_movies_bar(
    q: str = Query(..., min_length=1, description="Film Search"),
    limit: int = 5,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    logger.info("Searching movies by title: %s", q)
    q_norm = q.strip().lower()

    stmt = (
        select(Film)
        .where(Film.title.ilike(f"%{q_norm}%"))
        .order_by(Film.imdb_rating.desc(), Film.id)
        .offset(offset)
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()

@router.get("/unpopular", response_model=List[MovieHomeRead], summary="Read Unpopular Movies")
def read_unpopular_movies(db: Session = Depends(get_db), limit: int = 12):
    logger.info("Got request for popular movies with limit %s", limit)

    try:
        movies = get_unpopular_movies(db, limit=limit)
        logger.info("Successfully got %s popular movies with limit", len(movies))
        return movies
    except Exception as e:
        logger.error("Failed when getting popular movies: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/trending", response_model=List[MovieHomeRead])
def read_trending_movies(db: Session = Depends(get_db), limit: int = 12):
    current_year = datetime.now().year
    logger.info("Got request for trending movies with limit %s", limit)

    try:
        movies = get_top_movies_current_year(db, limit=limit)
        logger.info("Found %s top movies for %s year", len(movies), current_year)
        return movies
    except Exception as e:
        logger.error("Failed when getting top movies: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie_by_id(
    movie_id: int,
    db: Session = Depends(get_db)
):
    logger.info("Request for detail about movie with ID: %s", movie_id)

    stmt = select(Film).where(Film.id == movie_id)
    film = db.execute(stmt).scalar_one_or_none()

    if not film:
        logger.warning("Film with ID %s not found", movie_id)
        raise HTTPException(status_code=404, detail="Movie not found")

    genres_stmt = (
        select(Genre.genre_name)
        .join(FilmGenre, FilmGenre.genre_id == Genre.id)
        .where(FilmGenre.film_id == movie_id)
    )
    genres = list(db.execute(genres_stmt).scalars().all())

    people = (
        [p.strip() for p in film.people.split(",")]
        if film.people
        else []
    )

    return MovieDetailResponse(
        id=film.id,
        title=film.title,
        year=film.year,
        overview=film.overview,
        people=people,
        imdb_rating=film.imdb_rating,
        meta_score=film.meta_score,
        age_certification_id=film.age_certification_id,
        poster_path=film.poster_path,
        tmdb_id=film.tmdb_id,
        genres=genres
    )