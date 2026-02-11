from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

class QueryCreate(BaseModel):
    query_text: str = Field(..., min_length=2, max_length=500)
    @field_validator('query_text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Текст запиту не може складатися з пробілів")
        return v

class QueryRead(QueryCreate):
    id: int
    client_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)