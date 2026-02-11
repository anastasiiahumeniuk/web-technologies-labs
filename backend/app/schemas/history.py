from typing import Optional, List
from pydantic import ConfigDict, Field, BaseModel

class FilmInfo(BaseModel):
    id: int = Field(description="Movie ID")
    title: str
    year: Optional[int] = None
    imdb_rating: Optional[float] = None
    poster_path: Optional[str] = None


class QueryFilmInfo(BaseModel):
    film: FilmInfo
    similarity: float

    model_config = ConfigDict(from_attributes=True)

class HistoryItem(BaseModel):
    id: int = Field(description="Query ID")
    query_text: str = Field(validation_alias="query_text")
    results: List[QueryFilmInfo] = Field(
        validation_alias="film_associations",
        serialization_alias="results"
    )

    model_config = ConfigDict(from_attributes=True)