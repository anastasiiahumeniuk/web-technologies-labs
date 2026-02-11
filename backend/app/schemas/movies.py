from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class MovieResponse(BaseModel):
    id: int = Field(description="Movie ID")
    title: str
    year: Optional[int] = None
    imdb_rating: Optional[float] = None
    poster_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MovieDetailResponse(BaseModel):
    id: int
    title: str
    year: Optional[int]
    overview: Optional[str]
    people: List[str]
    imdb_rating: Optional[float]
    meta_score: Optional[int]
    age_certification_id: Optional[int]
    poster_path: Optional[str]
    tmdb_id: Optional[int]
    genres: List[str]

    model_config = ConfigDict(from_attributes=True)

class MovieHomeRead(BaseModel):
    id: int
    genres: str
    title: str
    poster_path: Optional[str] = None
    imdb_rating: float = Field(..., json_schema_extra={"example": "8.9"})
    year: Optional[int]

    model_config = ConfigDict(from_attributes=True)