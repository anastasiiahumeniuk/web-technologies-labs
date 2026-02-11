from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import UserQuery
from app.models.query_film import QueryFilm
from app.schemas.query import QueryCreate

def save_user_query(db: Session, client_id: int, query_data: QueryCreate) -> UserQuery:
    new_query = UserQuery(client_id=client_id, query_text=query_data.query_text)

    db.add(new_query)
    db.flush()
    db.refresh(new_query)
    return new_query

def save_query_result(db: Session, query_id: int, film_id: int, similarity: Decimal) -> QueryFilm:
    new_query_result = QueryFilm(query_id=query_id, film_id=film_id, similarity=similarity)

    db.add(new_query_result)

    return new_query_result
