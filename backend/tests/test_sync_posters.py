import pytest
from unittest.mock import AsyncMock, MagicMock

from scripts.sync_posters import process_posters, TMDB_IMAGE_BASE

@pytest.mark.asyncio
async def test_process_posters_success(mocker):
    class FakeFilm:
        def __init__(self):
            self.tmdb_id = 100
            self.poster_path = "/test.jpg"
            self.title = "Test film"

    fake_film = FakeFilm()
    fake_list = [fake_film]

    fake_session = MagicMock()
    mocker.patch("scripts.sync_posters.SessionLocal", return_value=fake_session)

    fake_execute = MagicMock()
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = fake_list
    fake_execute.scalars.return_value = fake_scalars
    fake_session.execute.return_value = fake_execute

    fake_client = AsyncMock()
    fake_client.get = AsyncMock(return_value=MagicMock(status_code=200, content=b"image-bytes"))
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None

    mocker.patch("scripts.sync_posters.httpx.AsyncClient", return_value=fake_client)

    upload_mock = mocker.patch(
        "scripts.sync_posters.upload_file_to_r2",
        return_value="movies/posters/100.jpg"
    )

    await process_posters()

    fake_client.get.assert_any_call(f"{TMDB_IMAGE_BASE}/test.jpg")
    upload_mock.assert_called_once()

    assert fake_film.poster_path == "movies/posters/100.jpg"
    fake_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_process_posters_download_fail(mocker):

    class FakeFilm:
        def __init__(self):
            self.tmdb_id = 777
            self.poster_path = "/broken.jpg"
            self.title = "Broken Film"

    fake_film = FakeFilm()
    fake_films_list = [fake_film]

    fake_session = MagicMock()
    mocker.patch("scripts.sync_posters.SessionLocal", return_value=fake_session)

    fake_execute = MagicMock()
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = fake_films_list
    fake_execute.scalars.return_value = fake_scalars
    fake_session.execute.return_value = fake_execute

    fake_client = AsyncMock()
    fake_client.get.return_value.status_code = 404
    fake_client.get.return_value.content = None

    mocker.patch("httpx.AsyncClient", return_value=fake_client)

    upload_mock = mocker.patch(
        "scripts.sync_posters.upload_file_to_r2"
    )

    await process_posters()

    upload_mock.assert_not_called()

    fake_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_download_with_retries_success(mocker):
    class FakeFilm:
        def __init__(self):
            self.tmdb_id = 100
            self.poster_path = "/retry.jpg"
            self.title = "Retry film"

    fake_film = FakeFilm()

    fake_session = MagicMock()
    mocker.patch("scripts.sync_posters.SessionLocal", return_value=fake_session)

    fake_execute = MagicMock()
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = [fake_film]
    fake_execute.scalars.return_value = fake_scalars
    fake_session.execute.return_value = fake_execute

    fake_client = AsyncMock()
    fake_response = MagicMock(status_code=200, content=b"image-bytes")

    fail_response = MagicMock(status_code=500, content="")
    fake_client.get = AsyncMock(side_effect=[fail_response, fail_response, fake_response, fake_response])
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None
    mocker.patch("scripts.sync_posters.httpx.AsyncClient", return_value=fake_client)

    upload_mock = mocker.patch(
        "scripts.sync_posters.upload_file_to_r2",
        return_value="movies/posters/100.jpg"
    )

    mocker.patch("asyncio.sleep", new=AsyncMock())

    await process_posters()

    assert fake_client.get.call_count == 4

    upload_mock.assert_called_once()

    assert fake_film.poster_path == "movies/posters/100.jpg"
    fake_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_process_posters_download_failure(mocker):
    class FakeFilm:
        def __init__(self):
            self.tmdb_id = 101
            self.poster_path = "/fail.jpg"
            self.title = "Fail film"

    fake_film = FakeFilm()
    fake_list = [fake_film]

    fake_session = MagicMock()
    mocker.patch("scripts.sync_posters.SessionLocal", return_value=fake_session)

    fake_execute = MagicMock()
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = fake_list
    fake_execute.scalars.return_value = fake_scalars
    fake_session.execute.return_value = fake_execute

    fake_client = AsyncMock()
    fail_response = MagicMock(status_code=500, content=b"")
    fake_client.get = AsyncMock(side_effect=[fail_response] * 3)
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None
    mocker.patch("scripts.sync_posters.httpx.AsyncClient", return_value=fake_client)

    upload_mock = mocker.patch(
        "scripts.sync_posters.upload_file_to_r2",
        return_value=None
    )

    mocker.patch("asyncio.sleep", new=AsyncMock())

    await process_posters()

    assert fake_client.get.call_count == 4

    upload_mock.assert_not_called()

    assert fake_film.poster_path == "/fail.jpg"

    fake_session.commit.assert_not_called()
