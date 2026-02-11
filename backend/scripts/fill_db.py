import asyncio
import os
import sys
import httpx
from sqlalchemy import select, func
from sqlalchemy.orm import configure_mappers
import time

sys.path.append(os.getcwd())
from app.database.sessions import SessionLocal
from app.models.film import Film
from dotenv import load_dotenv

configure_mappers()
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
MOVIES_LIMIT = 5000
CONCURRENCY = 5
RETRIES = 3
MOVIES_PER_PAGE = 20
MAX_PAGE = 500

MOVIE_ENDPOINTS = [
    "popular",
    "top_rated",
    "now_playing",
    "upcoming"
]

rating_to_id_mapping = {
    "0": 1, "0+": 1, "6": 2, "6+": 2,
    "12": 3, "12+": 3, "16": 4, "16+": 4,
    "18": 5, "18+": 5, "21": 5,
    "G": 1, "PG": 2, "PG-13": 3, "R": 4,
    "NC-17": 5, "NR": 1
}


def extract_age_rating(data: dict) -> int | None:
    releases = data.get("release_dates", {}).get("results", [])
    for region in ["UA", "US"]:
        for item in releases:
            if item["iso_3166_1"] == region:
                for release in item["release_dates"]:
                    cert = release.get("certification")
                    if cert and cert in rating_to_id_mapping:
                        return rating_to_id_mapping[cert]
    return None


async def safe_request(client, url, params, retries=RETRIES):
    for attempt in range(retries):
        try:
            resp = await client.get(url, params=params, timeout=15.0)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:  # Rate limit
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            print(f"Request failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(0.5 * (2 ** attempt))
    return None


async def get_movie_details(client, movie_id):
    resp = await safe_request(client, f"{BASE_URL}/movie/{movie_id}", {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA",
        "append_to_response": "release_dates"
    })
    if not resp:
        return None

    data = resp.json()
    overview = data.get("overview")
    if not overview:
        return None

    age_certification_id = extract_age_rating(data)
    if age_certification_id is None:
        return None

    credits_resp = await safe_request(client, f"{BASE_URL}/movie/{movie_id}/credits", {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA"
    })
    credits = credits_resp.json() if credits_resp else {}
    directors = [c['name'] for c in credits.get("crew", []) if c['job'] == "Director"]
    actors = [c['name'] for c in credits.get("cast", [])[:5]]
    people_str = ", ".join(directors + actors)
    genres_str = ", ".join([g['name'] for g in data.get("genres", [])])
    year = int(data.get("release_date", "0000")[:4]) if data.get("release_date") else None

    return {
        "tmdb_id": movie_id,
        "title": data.get("title"),
        "year": year,
        "overview": overview,
        "genres": genres_str,
        "people": people_str,
        "imdb_rating": data.get("vote_average"),
        "meta_score": 0.0,
        "age_certification_id": age_certification_id,
        "poster_path": data.get("poster_path"),
    }


async def fetch_page(client, db, endpoint, page, movies_saved, semaphore):
    async with semaphore:
        resp = await safe_request(client, f"{BASE_URL}/movie/{endpoint}", {
            "api_key": TMDB_API_KEY,
            "language": "uk-UA",
            "page": page
        })
        if not resp:
            print(f"Skipping {endpoint} page {page}")
            return 0

        results = resp.json().get("results", [])
        added = 0

        for item in results:
            if movies_saved[0] >= MOVIES_LIMIT:
                break

            tmdb_id = item["id"]
            existing = db.execute(select(Film).where(Film.tmdb_id == tmdb_id)).scalar_one_or_none()
            if existing:
                continue

            movie_data = await get_movie_details(client, tmdb_id)
            if movie_data:
                db.add(Film(**movie_data))
                try:
                    db.commit()
                    movies_saved[0] += 1
                    added += 1
                    print(f"Added ({movies_saved[0]}/{MOVIES_LIMIT}): {movie_data['title']} [{endpoint}]")
                except Exception as e:
                    print(f"Database error: {e}")
                    db.rollback()

            await asyncio.sleep(0.1)

        return added


async def main():
    if not TMDB_API_KEY:
        print("TMDB_API_KEY not found")
        return

    db = SessionLocal()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    movies_saved_count = db.execute(select(func.count(Film.tmdb_id))).scalar()
    movies_saved = [movies_saved_count]

    print(f"Movies in DB: {movies_saved_count}/{MOVIES_LIMIT}")

    if movies_saved_count >= MOVIES_LIMIT:
        print("Target already reached!")
        return

    start_time = time.time()

    async with httpx.AsyncClient() as client:
        for endpoint in MOVIE_ENDPOINTS:
            if movies_saved[0] >= MOVIES_LIMIT:
                break

            print(f"\nFetching from {endpoint} endpoint...")

            tasks = []
            for page in range(1, MAX_PAGE + 1):
                if movies_saved[0] >= MOVIES_LIMIT:
                    break
                tasks.append(fetch_page(client, db, endpoint, page, movies_saved, semaphore))

                if len(tasks) == 20 or page == MAX_PAGE:
                    await asyncio.gather(*tasks)
                    tasks = []
                    print(f"Progress: {movies_saved[0]}/{MOVIES_LIMIT} movies saved")

                    if movies_saved[0] >= MOVIES_LIMIT:
                        break

    elapsed_time = time.time() - start_time
    print(f"\nFinished! Total movies saved: {movies_saved[0]}/{MOVIES_LIMIT}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    db.close()


if __name__ == "__main__":
    asyncio.run(main())