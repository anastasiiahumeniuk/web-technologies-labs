import asyncio
import os
import sys
import httpx
from sqlalchemy import select
from dotenv import load_dotenv
from app.database.sessions import SessionLocal
from app.models.film import Film
from app.services.cloud_service import upload_file_to_r2

sys.path.append(os.getcwd())
load_dotenv()

TMDB_IMAGE_BASE = os.getenv("TMDB_IMAGE_BASE")

async def process_posters():
    db = SessionLocal()

    stmt = select(Film).where(
        Film.poster_path.like("/%"),
        Film.poster_path.is_not(None)
    )

    films_to_update = db.execute(stmt).scalars().all()

    print(f"Found {len(films_to_update)} posters for replacing in R2")

    if not films_to_update:
        print("All posters are synchronized!")
        return

    async def download_with_retry(client, url, retries=3, delay=1):
        for attempt in range(retries):
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.content
                print(f"Attempt {attempt + 1}: status {resp.status_code} for {url}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay * (2 ** attempt))
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        for film in films_to_update:
            tmdb_path = film.poster_path
            download_url = f"{TMDB_IMAGE_BASE}{tmdb_path}"

            try:
                image_data = await download_with_retry(client, download_url)

                await client.get(download_url)
                if not image_data:
                    print(f"Failed to download {download_url} after retries")
                    continue

                new_filename = f"movies/posters/{film.tmdb_id}.jpg"

                uploaded_key = upload_file_to_r2(image_data, new_filename)

                if uploaded_key:
                    film.poster_path = uploaded_key
                    db.commit()

            except Exception as e:
                print(f"Error with film {film.title}: {e}")
                db.rollback()

            await asyncio.sleep(0.5)

    db.close()

if __name__ == "__main__":
    asyncio.run(process_posters())