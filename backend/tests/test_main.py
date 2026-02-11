from app.main import app

def test_app_exists():
    assert app is not None
    assert hasattr(app, "routes")

def test_root_returns_404(client):
    response = client.get("/")
    assert response.status_code == 404

def test_movies_search_endpoint_exists(client):
    response = client.get("/movies/search", params={"q": "тест"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

