from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from app.database.sessions import get_db, engine
import logging

logger = logging.getLogger("http")


def warmup_db():
    url = make_url(str(engine.url))

    # Якщо тестова БД (SQLite), пропускаємо
    if url.drivername.startswith("sqlite"):
        logger.info("Skipping warmup for SQLite test DB")
        return

    logger.info("Warming up real database...")

    db = next(get_db())

    db.execute(text("SELECT 1"))

    db.execute(text("""
        SELECT 1 - (embedding <=> embedding)
        FROM vectors
        LIMIT 1
    """))

    db.execute(text("""
        SELECT f.id
        FROM film f
        JOIN vectors v ON v.film_id = f.id
        LEFT JOIN film_genre fg ON fg.film_id = f.id
        LEFT JOIN genre g ON g.id = fg.genre_id
        LIMIT 5
    """))

    db.close()
    logger.info("Database warmed up")
