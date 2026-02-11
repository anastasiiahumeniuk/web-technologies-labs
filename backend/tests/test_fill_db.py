import asyncio
import pytest
import respx
from httpx import AsyncClient, Response
from dotenv import load_dotenv
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

from scripts.fill_db import (extract_age_rating, get_movie_details, safe_request, fetch_page)

sys.path.append(os.getcwd())
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

@pytest.mark.parametrize("input_data,expected_id", [
    ({
        "release_dates": {
            "results": [
                {"iso_3166_1": "UA", "release_dates": [{"certification": "16"}]}
            ]
        }
    }, 4),

    ({
        "release_dates": {
            "results": [
                {"iso_3166_1": "US", "release_dates": [{"certification": "R"}]}
            ]
        }
    }, 4),

    ({
        "release_dates": {
            "results": [
                {"iso_3166_1": "UA", "release_dates": [{"certification": "12"}]},
                {"iso_3166_1": "US", "release_dates": [{"certification": "R"}]},
            ]
        }
    }, 3),

    ({
        "release_dates": {
            "results": [
                {"iso_3166_1": "US", "release_dates": [{"certification": "XX"}]}
            ]
        }
    }, None),

    ({}, None)
])
def test_extract_age_rating(input_data, expected_id):
    assert extract_age_rating(input_data) == expected_id

@pytest.mark.asyncio
@respx.mock
async def test_safe_request_success():
    url = 'https://example.com/api'
    respx.get(url).mock(return_value=Response(200, json={"ok": True}))

    async with AsyncClient() as client:
        resp = await safe_request(client, url, params={})

    assert resp is not None
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

@pytest.mark.asyncio
@respx.mock
async def test_safe_request_fail_error_429():
    url = 'https://example.com/api'
    route = respx.get(url).mock(side_effect=[
        Response(429),
        Response(200, json={"ok": False})
    ])

    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            resp = await safe_request(client, url, params={}, retries=3)

    assert resp.status_code == 200
    assert route.call_count == 2

@pytest.mark.asyncio
@respx.mock
async def test_safe_request_failure():
    url = 'https://example.com/api'
    respx.get(url).mock(return_value=Response(500))

    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            resp = await safe_request(client, url, params={}, retries=2)

    assert resp is None

@pytest.mark.asyncio
async def test_get_movie_details_success(respx_mock):
    movie_id = 1

    respx_mock.get(url__regex=f".*/movie/{movie_id}.*").mock(
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
                        {"iso_3166_1": "UA", "release_dates": [{"certification": "16"}]}
                    ]
                }
            }
        )
    )

    respx_mock.get(url__regex=f".*/movie/{movie_id}/credits.*").mock(
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
            }
        )
    )

    async with AsyncClient() as client:
        movie_data = await get_movie_details(client, movie_id)

    assert movie_data["title"] == "Сімейний план 2"
    assert movie_data["year"] == 2025
    assert movie_data["age_certification_id"] == 4
    assert movie_data["poster_path"] == "/xXPXJhrWLrSOBazPRftBkvgSCau.jpg"

@pytest.mark.asyncio
@respx.mock
async def test_get_movie_details_api_fail():
    movie_id = 1000
    respx.get(f"{BASE_URL}/movie/{movie_id}").mock(return_value=Response(404))
    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            movie_data = await get_movie_details(client, movie_id)

    assert movie_data is None

@pytest.mark.asyncio
@respx.mock
async def test_get_movie_details_no_overview():
    movie_id = 1
    respx.get(f"{BASE_URL}/movie/{movie_id}").mock(return_value=Response(
        200, json={
            "title": "Titanic",
            "overview": "",
            "release_date": {"results": []},
        }
    ))
    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            movie_data = await get_movie_details(client, movie_id)

    assert movie_data is None

@pytest.mark.asyncio
@respx.mock
async def test_get_movie_details_no_age():
    movie_id = 1
    respx.get(f"{BASE_URL}/movie/{movie_id}").mock(return_value=Response(
        200, json={
            "title": "Titanic",
            "overview": "This is cool film",
            "age_certification_id": None,
            "release_date": {"results": []},
        }
    ))
    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            movie_data = await get_movie_details(client, movie_id)

    assert movie_data is None

@pytest.mark.asyncio
@respx.mock
async def test_get_movie_details_credits_fail():
    movie_id = 1

    respx.get(f"{BASE_URL}/movie/{movie_id}").mock(return_value=Response(
        200, json={
            "title": "Titanic",
            "overview": "This is cool film",
            "release_date": "2023-01-01",
            "genres": "Drama",
            "vote_average": 6.678,
            "release_dates": {
                "results": [{"iso_3166_1": "US", "release_dates": [{"certification": "G"}]}],
            }
        })
    )

    respx.get(f"{BASE_URL}/movie/{movie_id}").mock(return_value=Response(500))

    with patch("asyncio.sleep", return_value=None):
        async with AsyncClient() as client:
            movie_data = await get_movie_details(client, movie_id)

    assert movie_data is None

@pytest.mark.asyncio
async def test_fetch_page_saves_movies(monkeypatch):
    fake_response = AsyncMock()
    fake_response.status_code = 200
    fake_response.json = lambda: {
        "results": [
            {"id": 1, "title": "Titanic"},
            {"id": 2, "title": "Batman"},
        ]
    }

    fake_client = AsyncMock()
    fake_client.get.return_value = fake_response

    async def fake_get_movie_details(client, movie_id):
        title_map = {1: "Titanic", 2: "Batman"}
        return {
            "tmdb_id": movie_id,
            "title": title_map[movie_id],
            "year": 1995,
            "overview": "This is cool film",
            "genres": "Drama",
            "people": "Director, Leonardo di Caprio",
            "imdb_rating": 7.5,
            "meta_score": 0.0,
            "age_certification_id": "12+",
            "poster_path": f"/poster{movie_id}.jpg",
        }

    monkeypatch.setattr('scripts.fill_db.get_movie_details', fake_get_movie_details)

    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.side_effect = [None, None]

    movies_saved = [0]

    semaphore = asyncio.Semaphore(1)

    added = await fetch_page(fake_client, fake_db, "popular", page=1, movies_saved=movies_saved, semaphore=semaphore)

    assert added == 2
    assert movies_saved == [2]
    assert fake_db.add.call_count == 2
    assert fake_db.commit.call_count == 2
    fake_client.get.assert_called()
