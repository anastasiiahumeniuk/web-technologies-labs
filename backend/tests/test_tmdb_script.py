import pytest
import respx
from httpx import AsyncClient, Response
import os
import sys
from scripts.fill_db import get_movie_details

sys.path.append(os.getcwd())

BASE_URL = os.getenv("BASE_URL", "https://api.themoviedb.org/3")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@pytest.mark.asyncio
@respx.mock
async def test_get_movie_details_success():
    movie_id = 1

    # Mock the movie details endpoint
    respx.get(
        f"{BASE_URL}/movie/{movie_id}",
        params={
            "api_key": TMDB_API_KEY,
            "language": "uk-UA",
            "append_to_response": "release_dates",
        }
    ).mock(
        return_value=Response(
            200,
            json={
                "title": "Сімейний план 2",
                "release_date": "2025-01-01",
                "overview": "Колишній кілер Ден на Різдво хоче тільки одного …",
                "genres": [{"name": "Бойовик"}, {"name": "Комедія"}],
                "poster_path": "/xXPXJhrWLrSOBazPRftBkvgSCau.jpg",
                "vote_average": 6.678,
                "release_dates": {
                    "results": [
                        {
                            "iso_3166_1": "UA",
                            "release_dates": [{"certification": "16"}],
                        }
                    ]
                },
            },
        )
    )

    # Mock the credits endpoint - FIX: Include language parameter
    respx.get(
        f"{BASE_URL}/movie/{movie_id}/credits",
        params={
            "api_key": TMDB_API_KEY,
            "language": "uk-UA"  # This was missing!
        }
    ).mock(
        return_value=Response(
            200,
            json={
                "crew": [{"job": "Director", "name": "Саймон Кехлан Джонс"}],
                "cast": [
                    {"name": "Марк Волберґ"},
                    {"name": "Мішель Монеген"},
                    {"name": "Кіт Герінґтон"},
                    {"name": "Зої Коллетті"},
                    {"name": "Van Crosby"},
                ],
            },
        )
    )

    async with AsyncClient() as client:
        movie_data = await get_movie_details(client, movie_id)

    assert movie_data is not None
    assert movie_data["title"] == "Сімейний план 2"
    assert movie_data["year"] == 2025
    assert movie_data["age_certification_id"] == 4
    assert movie_data["poster_path"] == "/xXPXJhrWLrSOBazPRftBkvgSCau.jpg"
    assert "Саймон Кехлан Джонс" in movie_data["people"]
    assert "Марк Волберґ" in movie_data["people"]