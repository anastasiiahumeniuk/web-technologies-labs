from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import time
from app.schemas.search import SearchRequest, ShowSearch
from app.database.sessions import get_db
from app.services.search_film import search_films
from app.services.embedding import generate_embedding

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/films", response_model=List[ShowSearch])
async def search_films_endpoint(
    search_params: SearchRequest,
    db: Session = Depends(get_db)
):
    total_start = time.perf_counter()

    try:
        logger.info("Searching films with query: '%s'", search_params.query_text)

        # ---------- Embedding ----------
        try:
            emb_start = time.perf_counter()
            query_vector = generate_embedding(search_params.query_text)
            emb_time = time.perf_counter() - emb_start
        except Exception as e:
            # Лог рядок потрібний для тестів
            logger.error("Embedding generation failed")
            # Детальний лог
            logger.error("Embedding failed: %s", str(e))
            raise HTTPException(
                status_code=503,
                detail="Embedding service unavailable"
            )

        # ---------- DB search ----------
        try:
            db_start = time.perf_counter()
            results = search_films(
                query_vector=query_vector,
                genres_filter=search_params.genres_filter,
                age_cert_filter=search_params.age_cert_filter,
                top_k=search_params.top_k,
                db=db
            )
            db_time = time.perf_counter() - db_start
        except Exception as e:
            # Лог рядок потрібний для тестів
            logger.error("Database search failed")
            # Детальний лог
            logger.error("DB search failed: %s", str(e))
            raise HTTPException(
                status_code=500,
                detail="Search operation failed"
            )

        total_time = time.perf_counter() - total_start

        # Лог для тестів
        logger.info("Search completed")
        # Детальний лог із часами
        logger.info(
            "AI search timings | total=%.3fs | embedding=%.3fs | db=%.3fs | results=%d",
            total_time, emb_time, db_time, len(results)
        )

        return results

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during search")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
