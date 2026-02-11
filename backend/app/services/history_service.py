from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models import UserQuery
from app.models.query_film import QueryFilm


def delete_all_queries(db: Session, client_id: int):
    stmt = (
        delete(UserQuery)
        .where(UserQuery.client_id == client_id)
        .returning(UserQuery.id)
    )

    deleted_ids = db.execute(stmt).scalars().all()

    db.commit()

    return len(deleted_ids)

def get_user_history_with_films(db: Session, user_id: int):
    stmt = (
        select(UserQuery)
        .where(UserQuery.client_id == user_id)
        .options(
            selectinload(UserQuery.film_associations)
            .joinedload(QueryFilm.film)
        )
        .order_by(UserQuery.created_at.desc())
    )
    return db.scalars(stmt).all()


def delete_selected_query(db: Session, query_id: int, client_id: int):
    stmt = (
        delete(UserQuery)
        .where(UserQuery.id == query_id)
        .where(UserQuery.client_id == client_id)
    )

    result = db.execute(stmt)

    db.commit()

    if result.rowcount == 0:
        return False

    return True