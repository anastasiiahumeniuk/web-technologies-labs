from enum import Enum

from pydantic import BaseModel, ConfigDict


class InteractionType(str, Enum):
    CLICK = "click"
    WATCH_LATER = "watch_later"
    LIKE = "like"

    REMOVE_LIKE = "remove_like"
    REMOVE_WATCH_LATER = "remove_watch_later"


class InteractionCreate(BaseModel):
    film_id: int
    action: InteractionType


class InteractionResponse(BaseModel):
    client_id: int
    film_id: int
    score: int
    is_liked: bool

    model_config = ConfigDict(from_attributes=True)