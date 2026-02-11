from app.services.film_service import get_unpopular_movies
from sqlalchemy.exc import OperationalError
import pytest

def test_get_popular_movies_calls_correct_methods(mocker):
    mock_db = mocker.Mock()

    mock_result = mocker.Mock()
    mock_db.execute.return_value = mock_result
    mock_result.scalars.return_value.all.return_value = [
        {"id": 1, "title": "Жахи", "imdb_rating": 3},
        {"id": 2, "title": "Нереальний блокбастер", "imdb_rating": 3.2}
    ]

    limit = 12
    result = get_unpopular_movies(db=mock_db, limit=limit)
    mock_db.execute.assert_called_once()

    assert len(result) == 2
    assert result[0]["title"] == "Жахи"

def test_get_popular_movies_default_limit(mocker):
    mock_db = mocker.Mock()
    mock_result = mocker.Mock()
    mock_db.execute.return_value = mock_result
    mock_result.scalars.return_value.all.return_value = []

    get_unpopular_movies(db=mock_db)

    called_stmt = mock_db.execute.call_args[0][0]
    assert called_stmt._limit == 12

def test_get_popular_movies_db_connection_error(mocker):
    mock_db = mocker.Mock()

    mock_db.execute.side_effect = OperationalError("psycopg2.OperationalError", params=None, orig=None)
    with pytest.raises(OperationalError):
        get_unpopular_movies(db=mock_db, limit=12)

    mock_db.execute.assert_called_once()
