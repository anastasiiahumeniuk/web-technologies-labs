import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.sessions import get_db
from app.models.client import Client
from app.models.film import Film
from app.models.client_interaction import ClientInteraction
from app.schemas.interactions import InteractionResponse, InteractionCreate
from app.schemas.movies import MovieResponse
from app.services.interactions_service import InteractionService
from app.utils.dependencies import get_current_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("/", response_model=InteractionResponse)
def post_interaction(
    interaction_data: InteractionCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
):
    return InteractionService.register_interaction(
        db=db,
        client_id=current_client.id,
        film_id=interaction_data.film_id,
        action=interaction_data.action,
    )


@router.get(
    "/liked",
    response_model=List[MovieResponse],
    summary="Get liked films",
)
def get_liked_films(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
):
    films = (
        db.query(Film)
        .join(ClientInteraction, ClientInteraction.film_id == Film.id)
        .filter(
            ClientInteraction.client_id == current_client.id,
            ClientInteraction.is_liked.is_(True),
        )
        .all()
    )

    return films


@router.get(
    "/watch-later",
    response_model=List[MovieResponse],
    summary="Get watch later films",
)
def get_watch_later_films(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
):
    films = (
        db.query(Film)
        .join(ClientInteraction, ClientInteraction.film_id == Film.id)
        .filter(
            ClientInteraction.client_id == current_client.id,
            ClientInteraction.score == 5,
            ClientInteraction.is_liked.is_(False),
        )
        .all()
    )

    return films