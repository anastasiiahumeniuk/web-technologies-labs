from unittest.mock import MagicMock
import pytest
from app.models.film import Film
from app.schemas.movies import MovieResponse
from app.services.film_service import get_unpopular_movies


def test_format_film_return_formated_film():
    """Test MovieResponse validation with complete film data."""
    film = Film(
        id=1,
        title="Початок",
        year=2010,
        imdb_rating=8.8
    )
    result = MovieResponse.model_validate(film)
    assert isinstance(result, MovieResponse)
    assert result.id == 1
    assert result.title == "Початок"
    assert result.year == 2010


def test_format_film_return_none():
    """Test MovieResponse validation with None year."""
    film = Film(
        id=1,
        title="Початок",
        year=None,
        imdb_rating=8.8
    )

    result = MovieResponse.model_validate(film)

    assert result.year is None
    assert result.title is not None
    assert result.id == 1


@pytest.fixture(scope="function")
def seed_movies(db_session):
    """Seed database with test movies."""
    movies = [
        Film(title="Аватар", year=2009, imdb_rating=7.8),
        Film(title="Аватар: Шлях води", year=2022, imdb_rating=8.2),
        Film(title="Аватар: Вогонь і Попіл", year=2025, imdb_rating=9.0),
        Film(title="Месники: Завершення", year=2019, imdb_rating=8.4),
        Film(title="Темний лицар", year=2008, imdb_rating=9.0),
        Film(title="Похмурі тіні", year=2012, imdb_rating=6.2),
        Film(title="Бетмен: Початок", year=2005, imdb_rating=8.2),
        Film(title="Бетмен", year=2014, imdb_rating=7.0),
    ]
    db_session.add_all(movies)
    db_session.commit()
    return movies


def test_search_startswith_priority(client, seed_movies):
    """Test that search prioritizes titles starting with query."""
    response = client.get("/movies/search", params={"q": "Темний"})
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert data[0]["title"].startswith("Темний")


def test_search_contains(client, seed_movies):
    """Test that search finds movies containing query."""
    response = client.get("/movies/search", params={"q": "Бетмен"})
    assert response.status_code == 200

    titles = [m["title"] for m in response.json()]
    assert "Бетмен" in titles
    assert "Бетмен: Початок" in titles


def test_sorted_by_rating_desc(client, seed_movies):
    """Test that search results are sorted by rating descending."""
    response = client.get("/movies/search", params={"q": "Бетмен"})
    data = response.json()

    rating_order = [
        "Бетмен: Початок",
        "Бетмен",
    ]

    assert data[0]["title"] == rating_order[0]


def test_search_with_limit(client, seed_movies):
    """Test search with limit parameter."""
    response = client.get("/movies/search", params={"q": "Аватар", "limit": 3})
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"].startswith("Аватар")


def test_search_no_result(client, seed_movies):
    """Test search returns empty list when no results found."""
    response = client.get("/movies/search", params={"q": "Неіснуючий фільм"})
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_search_empty_query(client, seed_movies):
    """Test that empty query returns validation error."""
    response = client.get("/movies/search", params={"q": ""})
    assert response.status_code == 422


def test_search_case_insensitive(client, seed_movies):
    """Test that search is case insensitive."""
    response = client.get("/movies/search", params={"q": "аваТАР"})
    data = response.json()
    assert len(data) > 0
    assert all("Аватар" in m["title"] for m in data)


def test_response_model(client, seed_movies):
    """Test that search response contains required fields."""
    response = client.get("/movies/search", params={"q": "Темний"})
    data = response.json()
    for movie in data:
        assert "id" in movie
        assert "title" in movie
        assert "year" in movie


def test_get_movie_by_id_success(client):
    """Test successful retrieval of movie by ID."""
    mock_film = Film(
        id=1,
        title="The Matrix",
        year=1999,
        overview="A computer hacker learns about the true nature of reality.",
        people="Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
        imdb_rating=8.7,
        meta_score=73,
        age_certification_id=3,
        poster_path="/path/to/poster.jpg",
        tmdb_id=603
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = ["Action", "Sci-Fi"]

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/1")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "The Matrix"
        assert data["year"] == 1999
        assert data["overview"] == "A computer hacker learns about the true nature of reality."
        assert data["imdb_rating"] == 8.7
        assert data["meta_score"] == 73
        assert data["age_certification_id"] == 3
        assert data["poster_path"] == "/path/to/poster.jpg"
        assert data["tmdb_id"] == 603
        assert isinstance(data["people"], list)
        assert len(data["people"]) == 3
        assert "Keanu Reeves" in data["people"]
        assert isinstance(data["genres"], list)
        assert "Action" in data["genres"]
        assert "Sci-Fi" in data["genres"]
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_not_found(client):
    """Test retrieval of non-existent movie returns 404."""
    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = None

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_film_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_no_people(client):
    """Test movie with no people field (None)."""
    mock_film = Film(
        id=2,
        title="Test Movie",
        year=2020,
        overview="A test movie",
        people=None,
        imdb_rating=7.5,
        meta_score=65,
        age_certification_id=2,
        poster_path="/test.jpg",
        tmdb_id=123
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = ["Drama"]

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/2")

        assert response.status_code == 200
        data = response.json()
        assert data["people"] == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_empty_people(client):
    """Test movie with empty people string."""
    mock_film = Film(
        id=3,
        title="Test Movie",
        year=2020,
        overview="A test movie",
        people="",
        imdb_rating=7.5,
        meta_score=65,
        age_certification_id=2,
        poster_path="/test.jpg",
        tmdb_id=123
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = []

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/3")

        assert response.status_code == 200
        data = response.json()
        assert data["people"] == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_no_genres(client):
    """Test movie with no associated genres."""
    mock_film = Film(
        id=4,
        title="Unclassified Movie",
        year=2021,
        overview="No genre",
        people="John Doe",
        imdb_rating=6.0,
        meta_score=50,
        age_certification_id=1,
        poster_path="/unclassified.jpg",
        tmdb_id=456
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = []

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/4")

        assert response.status_code == 200
        data = response.json()
        assert data["genres"] == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_people_with_spaces(client):
    """Test that people names are properly stripped of whitespace."""
    mock_film = Film(
        id=5,
        title="Spacing Test",
        year=2022,
        overview="Test spacing",
        people=" Actor One , Actor Two , Actor Three ",
        imdb_rating=7.0,
        meta_score=60,
        age_certification_id=2,
        poster_path="/spacing.jpg",
        tmdb_id=789
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = ["Comedy"]

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/5")

        assert response.status_code == 200
        data = response.json()
        assert "Actor One" in data["people"]
        assert "Actor Two" in data["people"]
        assert "Actor Three" in data["people"]
        for person in data["people"]:
            assert person == person.strip()
    finally:
        client.app.dependency_overrides.clear()


def test_get_movie_by_id_invalid_id(client):
    """Test with invalid movie ID (non-integer)."""
    response = client.get("/movies/invalid")
    assert response.status_code == 422


def test_get_movie_by_id_optional_fields_none(client):
    """Test movie with optional fields set to None."""
    mock_film = Film(
        id=6,
        title="Minimal Movie",
        year=None,
        overview=None,
        people=None,
        imdb_rating=None,
        meta_score=None,
        age_certification_id=None,
        poster_path=None,
        tmdb_id=None
    )

    mock_film_result = MagicMock()
    mock_film_result.scalar_one_or_none.return_value = mock_film

    mock_genres_result = MagicMock()
    mock_genres_result.scalars.return_value.all.return_value = []

    mock_db_session = MagicMock()
    mock_db_session.execute.side_effect = [mock_film_result, mock_genres_result]

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies/6")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Movie"
        assert data["year"] is None
        assert data["overview"] is None
        assert data["people"] == []
        assert data["genres"] == []
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_no_filters(client):
    """Test getting movies without any filters."""
    mock_films = [
        Film(
            id=1,
            title="Movie 1",
            year=2023,
            overview="Overview 1",
            people="Actor 1",
            imdb_rating=8.5,
            meta_score=80,
            age_certification_id=1,
            poster_path="/poster1.jpg",
            tmdb_id=101
        ),
        Film(
            id=2,
            title="Movie 2",
            year=2022,
            overview="Overview 2",
            people="Actor 2",
            imdb_rating=7.5,
            meta_score=70,
            age_certification_id=2,
            poster_path="/poster2.jpg",
            tmdb_id=102
        )
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == "Movie 1"
        assert data[1]["title"] == "Movie 2"
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_filter_by_genre(client):
    """Test filtering movies by genre."""
    mock_films = [
        Film(
            id=1,
            title="Action Movie",
            year=2023,
            overview="Action",
            people="Actor",
            imdb_rating=8.0,
            meta_score=75,
            age_certification_id=1,
            poster_path="/action.jpg",
            tmdb_id=201
        )
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?genres=Action")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Action Movie"
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_filter_by_year(client):
    """Test filtering movies by year."""
    mock_films = [
        Film(id=1, title="2023 Movie", year=2023, overview="", people="",
             imdb_rating=8.0, meta_score=75, age_certification_id=1,
             poster_path="/test.jpg", tmdb_id=401)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?year=2023")

        assert response.status_code == 200
        data = response.json()
        assert all(movie["year"] == 2023 for movie in data)
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_filter_by_min_rating(client):
    """Test filtering movies by minimum rating."""
    mock_films = [
        Film(id=1, title="High Rated", year=2023, overview="", people="",
             imdb_rating=9.0, meta_score=90, age_certification_id=1,
             poster_path="/test.jpg", tmdb_id=501)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?min_rating=8.0")

        assert response.status_code == 200
        data = response.json()
        assert all(movie["imdb_rating"] >= 8.0 for movie in data)
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_filter_by_age_certification(client):
    """Test filtering movies by age certification."""
    mock_films = [
        Film(id=1, title="PG Movie", year=2023, overview="", people="",
             imdb_rating=7.0, meta_score=70, age_certification_id=1,
             poster_path="/test.jpg", tmdb_id=601)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?age_certification=PG")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_combined_filters(client):
    """Test combining multiple filters."""
    mock_films = [
        Film(id=1, title="Filtered Movie", year=2023, overview="", people="",
             imdb_rating=8.5, meta_score=85, age_certification_id=1,
             poster_path="/test.jpg", tmdb_id=701)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?genres=Action&year=2023&min_rating=8.0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_pagination(client):
    """Test pagination with limit and offset."""
    mock_films = [
        Film(id=i, title=f"Movie {i}", year=2023, overview="", people="",
             imdb_rating=8.0, meta_score=80, age_certification_id=1,
             poster_path=f"/movie{i}.jpg", tmdb_id=800 + i)
        for i in range(10, 20)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_films

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?limit=10&offset=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
    finally:
        client.app.dependency_overrides.clear()


def test_get_movies_list_empty_result(client):
    """Test when no movies match the filters."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db_session = MagicMock()
    mock_db_session.execute.return_value = mock_result

    def override_get_db():
        yield mock_db_session

    from app.database.sessions import get_db

    client.app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/movies?year=1800")

        assert response.status_code == 200
        assert response.json() == []
    finally:
        client.app.dependency_overrides.clear()

def test_get_unpopular_movies(client, mocker):
    """Test getting unpopular movies returns mocked result."""
    mock_movies = [
        {
            "id": 1,
            "title": "Low rated movie 1",
            "year": 2020,
            "imdb_rating": 3.2,
            "genres": "Бойовик"
        },
        {
            "id": 2,
            "title": "Low rated movie 2",
            "year": 2020,
            "imdb_rating": 3.2,
            "genres": "Драма"
        }
    ]

    mocker.patch(
        "app.routers.movies.get_unpopular_movies",
        return_value=mock_movies
    )

    response = client.get("/movies/unpopular?limit=2")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Low rated movie 1"

def test_get_unpopular_movies_failed(client, mocker):
    """Test getting unpopular movies returns 500 on service error"""

    mocker.patch(
        "app.routers.movies.get_unpopular_movies",
        side_effect=Exception("DB error")
    )

    response = client.get("/movies/unpopular?limit=2")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}

def test_read_trending_movies_success(client, mocker):
    """Test getting trending movies returns status code 200"""
    mock_movies = [
        {
            "id": 1,
            "title": "Top Movie 1",
            "year": 2026,
            "imdb_rating": 9.2,
            "genres": "Drama"
        },
        {
            "id": 2,
            "title": "Movie 2",
            "year": 2026,
            "imdb_rating": 9.1,
            "genres": "Drama"
        }
    ]

    mocker.patch(
        "app.routers.movies.get_top_movies_current_year",
        return_value=mock_movies
    )
    response = client.get("/movies/trending?limit=2")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Top Movie 1"

def test_read_trending_movies_failed(client, mocker):
    """Test getting trending movies returns 500 on service error"""

    mocker.patch(
        "app.routers.movies.get_top_movies_current_year",
        side_effect=Exception("DB error")
    )

    response = client.get("/movies/trending?limit=2")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}