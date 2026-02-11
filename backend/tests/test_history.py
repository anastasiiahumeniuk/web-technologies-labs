import pytest
from dataclasses import dataclass
from typing import List, Optional
from fastapi.testclient import TestClient
from app.main import app
from app.utils.dependencies import get_current_client
from app.models import Client
from app.schemas.history import HistoryItem

@dataclass
class MockFilm:
    id: int
    title: str
    year: Optional[int] = 2023
    imdb_rating: Optional[float] = 8.5
    poster_path: Optional[str] = "/test/path.jpg"


@dataclass
class MockQueryFilm:
    film: MockFilm
    similarity: float


@dataclass
class MockUserQuery:
    id: int
    query_text: str
    film_associations: List[MockQueryFilm]


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_auth():

    def mock_get_current_client():
        return Client(id=1, email="test@example.com")

    app.dependency_overrides[get_current_client] = mock_get_current_client

    yield
    app.dependency_overrides = {}


def test_get_my_history_router(client, mocker):
    mock_service = mocker.patch("app.routers.history.get_user_history_with_films")

    film_obj = MockFilm(id=101, title="Matrix")
    assoc_obj = MockQueryFilm(film=film_obj, similarity=0.99)
    user_query_obj = MockUserQuery(
        id=1,
        query_text="sci-fi",
        film_associations=[assoc_obj]
    )

    mock_service.return_value = [user_query_obj]

    response = client.get("/history/show")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["results"][0]["film"]["title"] == "Matrix"


def test_delete_all_router(client, mocker):
    mock_service = mocker.patch("app.routers.history.delete_all_queries")
    mock_service.return_value = 5

    response = client.delete("/history/delete/all")

    assert response.status_code == 200
    assert response.json()["deleted_count"] == 5
    assert "Successfully deleted" in response.json()["message"]


def test_delete_query_success_router(client, mocker):
    mock_service = mocker.patch("app.routers.history.delete_selected_query")
    mock_service.return_value = True

    response = client.delete("/history/delete/123")

    assert response.status_code == 204
    mock_service.assert_called_once()


def test_delete_query_not_found_router(client, mocker):
    mock_service = mocker.patch("app.routers.history.delete_selected_query")
    mock_service.return_value = False

    response = client.delete("/history/delete/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Query not found or access denied"


def test_delete_query_internal_error(client, mocker):
    mock_service = mocker.patch("app.routers.history.delete_selected_query")
    mock_service.side_effect = Exception("Database is down")

    response = client.delete("/history/delete/1")

    assert response.status_code == 500
    assert response.json()["detail"] == "An internal error occurred."