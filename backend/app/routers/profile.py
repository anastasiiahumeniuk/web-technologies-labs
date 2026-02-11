from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.sessions import get_db
from app.models.client import Client
from app.schemas.profile import ProfileResponse
from app.utils.dependencies import get_current_client

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=ProfileResponse, summary="Get current user profile")
def get_my_profile(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client),
):
    # db тут можна навіть не юзати, але лишаємо як стандарт
    return current_client
