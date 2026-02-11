import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from app.database.sessions import get_db
from app.models import Client
from app.schemas.history import HistoryItem
from app.services.history_service import delete_all_queries, get_user_history_with_films, delete_selected_query
from app.utils.dependencies import get_current_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history" ,tags=["History"])

@router.get("/show", response_model=List[HistoryItem])
def get_my_history(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    try:
        result = get_user_history_with_films(db, user_id=current_client.id)

    except Exception as e:
        logging.error(f"Getting history for client {current_client.id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while selecting history"
        )

    return result

@router.delete("/delete/all", status_code=status.HTTP_200_OK)
def delete_all(
        db: Session = Depends(get_db),
        current_client: Client = Depends(get_current_client)
):
    try:
        delete_count = delete_all_queries(db, current_client.id)

    except Exception as e:
        logging.error(f"Deletion of history for client {current_client.id} failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting history"
        )

    return {
        "message": f"Successfully deleted history for user: {current_client.id}",
        "deleted_count": delete_count
    }


@router.delete("/delete/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_query(
        query_id: int,
        db: Session = Depends(get_db),
        current_client: Client = Depends(get_current_client)
):
    try:
        deleted = delete_selected_query(
            db,
            query_id=query_id,
            client_id=current_client.id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found or access denied"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred."
        )