from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class SearchRequest(BaseModel):
    query_text: str = Field(..., description="User's search query (genres, description, actors, etc.)")
    genres_filter: Optional[List[str]] = Field(None, description="List of genres to filter by")
    age_cert_filter: Optional[str] = Field(None, description="Age certification filter (e.g., '16+', '18+')")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    save_history: bool = Field(False, description="Save history of results for authorized user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query_text": "Action movie with Tom Cruise about spies and missions",
                "genres_filter": ["Action", "Thriller"],
                "age_cert_filter": "16+",
                "top_k": 10
            }
        }
    )

class ShowSearch(BaseModel):
    id: int
    title: str
    year: Optional[int]
    overview: Optional[str]
    poster_path: Optional[str]
    age_cert: Optional[str]
    genres: List[str]
    similarity: float

    model_config = ConfigDict(from_attributes=True)
