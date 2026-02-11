from app.services.query_service import save_user_query, save_query_result
from app.utils.dependencies import get_current_client
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from app.schemas.search import SearchRequest, ShowSearch
from app.models.client import Client
from app.schemas.query import QueryCreate
from app.database.sessions import get_db
from app.services.search_film import search_films
from app.services.embedding import generate_embedding

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

# Saving query and it`s result for user
def log_search_history_task(
    db: Session,
    client_id: int,
    query_text: str,
    results: List[ShowSearch]
):
    try:
        query_data = QueryCreate(query_text=query_text)
        user_query = save_user_query(db, client_id, query_data)

        if results:
            for film in results:
                sim_score = getattr(film, 'similarity', 0.0)
                save_query_result(
                    db=db,
                    query_id=user_query.id,
                    film_id=film.id,
                    similarity=Decimal(str(sim_score))
                )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save search history in background: {e}")
        db.rollback()


# Endpoint for vectorized search for authorized users
@router.post("/auth/films", response_model=List[ShowSearch])
async def search_films_authorized(
        search_params: SearchRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_client: Client = Depends(get_current_client)
):
    # Error catch
    try:
        # Embedding description
        query_vector = generate_embedding(search_params.query_text)

        # Executing general search
        results = search_films(
            query_vector=query_vector,
            genres_filter=search_params.genres_filter,
            age_cert_filter=search_params.age_cert_filter,
            top_k=search_params.top_k,
            db=db
        )
        # Raising an error if no results were found
        if not results:
            logger.warning(f"No results found for query: {search_params.query_text}")
            raise HTTPException(status_code=404, detail="No results")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")

    # Checking saving parameter
    if search_params.save_history:
        # Saving results as a background task
        background_tasks.add_task(
            log_search_history_task,
            db,
            current_client.id,
            search_params.query_text,
            results
        )

    return results if results else []