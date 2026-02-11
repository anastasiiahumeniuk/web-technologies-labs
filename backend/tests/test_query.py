import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.utils.dependencies import get_current_client
from app.models.client import Client
from app.schemas.search import ShowSearch

client = TestClient(app)

@pytest.fixture
def mock_user_auth():
    fake_client = Client(id=1, email="user123@example.com")
    app.dependency_overrides[get_current_client] = lambda: fake_client
    yield fake_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_search_results():
    return [
        ShowSearch(
            id=101,
            title="Титанік",
            year=1997,
            overview="Корабель тоне",
            poster_path="/path/to/poster.jpg",
            age_cert="PG-13",
            genres=["Drama", "Romance"],
            similarity=0.95
        ),
        ShowSearch(
            id=102,
            title="Аватар",
            year=2009,
            overview="Сині люди",
            poster_path="/path/to/avatar.jpg",
            age_cert="PG-13",
            genres=["Sci-Fi"],
            similarity=0.88
        )
    ]


def test_search_films_authorized_save_history_true(mocker, mock_user_auth, mock_search_results):
    mocker.patch("app.routers.query.generate_embedding", return_value="0.1,0.2,0.3")
    mocker.patch("app.routers.query.search_films", return_value=mock_search_results)

    mock_saved_query = mocker.Mock()
    mock_saved_query.id = 555

    mock_save_query_func = mocker.patch("app.routers.query.save_user_query", return_value=mock_saved_query)
    mock_save_result_func = mocker.patch("app.routers.query.save_query_result")

    payload = {
        "query_text": "фільм про кохання",
        "top_k": 5,
        "save_history": True
    }

    response = client.post("/search/auth/films", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Титанік"

    mock_save_query_func.assert_called_once()
    assert mock_save_result_func.call_count == 2

    call_args = mock_save_result_func.call_args_list[0]
    assert call_args[1]['query_id'] == 555
    assert call_args[1]['film_id'] == 101
    assert isinstance(call_args[1]['similarity'], Decimal)


def test_search_films_authorized_save_history_false(mocker, mock_user_auth, mock_search_results):

    mocker.patch("app.routers.query.generate_embedding", return_value="0.1,0.2")
    mocker.patch("app.routers.query.search_films", return_value=mock_search_results)

    mock_save_query_func = mocker.patch("app.routers.query.save_user_query")
    mock_save_result_func = mocker.patch("app.routers.query.save_query_result")

    payload = {
        "query_text": "швидкий пошук",
        "save_history": False
    }

    response = client.post("/search/auth/films", json=payload)

    assert response.status_code == 200

    mock_save_query_func.assert_not_called()
    mock_save_result_func.assert_not_called()


def test_search_films_background_task_failure(mocker, mock_user_auth, mock_search_results):

    mocker.patch("app.routers.query.generate_embedding", return_value="0.1,0.2")
    mocker.patch("app.routers.query.search_films", return_value=mock_search_results)

    mocker.patch("app.routers.query.save_user_query", side_effect=Exception("Deadlock or DB Error"))

    payload = {
        "query_text": "фільм",
        "save_history": True
    }

    response = client.post("/search/auth/films", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Титанік"



def test_search_films_no_results(mocker, mock_user_auth):
    mocker.patch("app.routers.query.generate_embedding", return_value="0.1,0.1")
    mocker.patch("app.routers.query.search_films", return_value=[])

    mock_save_query = mocker.patch("app.routers.query.save_user_query")

    payload = {"query_text": "щось неіснуюче", "save_history": True}
    response = client.post("/search/auth/films", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "No results"

    mock_save_query.assert_not_called()


def test_search_films_main_service_error(mocker, mock_user_auth):
    mocker.patch("app.routers.query.generate_embedding", return_value="0.1,0.1")

    mocker.patch("app.routers.query.search_films", side_effect=Exception("Search Service Down"))

    payload = {"query_text": "test"}
    response = client.post("/search/auth/films", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Search operation failed"