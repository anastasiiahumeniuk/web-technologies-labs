from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.sessions import get_db
from app.schemas.movies import MovieHomeRead
from app.services.film_service import get_popular_movies

router = APIRouter(prefix="/", tags=["Home"])

@router.get("/popular", response_model=List[MovieHomeRead])
def read_popular_movies(db: Session = Depends(get_db), limit: int = 12):

    movies = get_popular_movies(db, limit=limit)
    return movies

