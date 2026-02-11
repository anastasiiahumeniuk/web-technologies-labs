from app.schemas.search import ShowSearch


def test_search_films_success(client, mocker):
    """Test successful film search with mocked dependencies."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[
            ShowSearch(
                id=1,
                title="Test Movie",
                year=2023,
                overview="A test movie about testing",
                poster_path="/posters/test-movie.jpg",  # <--- ДОДАНО
                age_cert="16+",
                genres=["Drama", "Action"],
                similarity=0.85
            )
        ]
    )

    payload = {
        "query_text": "Action movie",
        "genres_filter": [],
        "age_cert_filter": "16+",
        "top_k": 10
    }

    response = client.post("/search/films", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    film = data[0]
    assert film["id"] == 1
    assert film["title"] == "Test Movie"
    assert film["year"] == 2023
    assert film["overview"] == "A test movie about testing"
    assert film["poster_path"] == "/posters/test-movie.jpg"  # <--- ДОДАНО
    assert isinstance(film["similarity"], float)
    assert film["similarity"] == 0.85
    assert film["age_cert"] == "16+"
    assert isinstance(film["genres"], list)
    assert "Drama" in film["genres"]
    assert "Action" in film["genres"]


def test_search_films_with_null_poster(client, mocker):
    """Test search with movie that has no poster."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[
            ShowSearch(
                id=2,
                title="No Poster Movie",
                year=2022,
                overview="Movie without poster",
                poster_path=None,  # <--- NULL poster
                age_cert="PG",
                genres=["Comedy"],
                similarity=0.75
            )
        ]
    )

    response = client.post(
        "/search/films",
        json={"query_text": "funny movie"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["poster_path"] is None


def test_search_films_logging(client, mocker, caplog):
    """Test that search endpoint logs requests and responses."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[]
    )

    with caplog.at_level("INFO"):
        response = client.post(
            "/search/films",
            json={"query_text": "test logging", "top_k": 3}
        )

    assert response.status_code == 200
    assert "Searching films with query" in caplog.text
    assert "Search completed" in caplog.text


def test_search_films_database_error(client, mocker, caplog):
    """Test that database search errors return 500."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        side_effect=Exception("DB fault")
    )

    with caplog.at_level("ERROR"):
        response = client.post(
            "/search/films",
            json={"query_text": "error test"}
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Search operation failed"
    assert "Database search failed" in caplog.text


def test_search_embedding_failure(client, mocker, caplog):
    """Test handling of embedding generation failure returns 503."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        side_effect=Exception("Embedding API down")
    )

    with caplog.at_level("ERROR"):
        response = client.post(
            "/search/films",
            json={"query_text": "test"}
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Embedding service unavailable"
    assert "Embedding generation failed" in caplog.text


def test_search_empty_results(client, mocker):
    """Test search with no matching results."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[]
    )

    response = client.post(
        "/search/films",
        json={"query_text": "nonexistent movie"}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_search_films_multiple_results(client, mocker):
    """Test search returning multiple films."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[
            ShowSearch(
                id=1,
                title="Movie One",
                year=2023,
                overview="First movie",
                poster_path="/poster1.jpg",
                age_cert="PG",
                genres=["Action"],
                similarity=0.95
            ),
            ShowSearch(
                id=2,
                title="Movie Two",
                year=2022,
                overview="Second movie",
                poster_path="/poster2.jpg",
                age_cert="PG-13",
                genres=["Drama"],
                similarity=0.85
            ),
            ShowSearch(
                id=3,
                title="Movie Three",
                year=2021,
                overview="Third movie",
                poster_path=None,
                age_cert="R",
                genres=["Horror"],
                similarity=0.75
            )
        ]
    )

    response = client.post(
        "/search/films",
        json={"query_text": "exciting movies", "top_k": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Перевіряємо що всі фільми мають необхідні поля
    for film in data:
        assert "id" in film
        assert "title" in film
        assert "poster_path" in film
        assert "similarity" in film


def test_search_films_with_filters(client, mocker):
    """Test search with genre and age certification filters."""
    mocker.patch(
        "app.routers.search.generate_embedding",
        return_value=[0.1, 0.2, 0.3]
    )

    mocker.patch(
        "app.routers.search.search_films",
        return_value=[
            ShowSearch(
                id=1,
                title="Filtered Movie",
                year=2023,
                overview="Matches filters",
                poster_path="/filtered.jpg",
                age_cert="PG-13",
                genres=["Action", "Sci-Fi"],
                similarity=0.90
            )
        ]
    )

    payload = {
        "query_text": "space adventure",
        "genres_filter": ["Sci-Fi"],
        "age_cert_filter": "PG-13",
        "top_k": 10
    }

    response = client.post("/search/films", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["age_cert"] == "PG-13"
    assert "Sci-Fi" in data[0]["genres"]