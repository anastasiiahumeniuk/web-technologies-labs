from decimal import Decimal
from app.services.query_service import save_user_query, save_query_result
from app.schemas.query import QueryCreate
from app.models import UserQuery
from app.models.query_film import QueryFilm


# Testing saving data into query table
def test_save_user_query_success(mocker):
    mock_db = mocker.Mock()

    client_id = 1
    query_data = QueryCreate(
        query_text="Фільм про штучний інтелект"
    )

    result = save_user_query(db=mock_db, client_id=client_id, query_data=query_data)

    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    mock_db.refresh.assert_called_once_with(result)

    assert isinstance(result, UserQuery)
    assert result.client_id == client_id
    assert result.query_text == "Фільм про штучний інтелект"


# Testing saving data into query_film table
def test_save_query_result_success(mocker):
    mock_db = mocker.Mock()

    query_id = 100
    film_id = 50
    similarity = Decimal("0.9876")

    save_query_result(db=mock_db, query_id=query_id, film_id=film_id, similarity=similarity)

    mock_db.add.assert_called_once()

    mock_db.flush.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()

    saved_obj = mock_db.add.call_args[0][0]
    assert isinstance(saved_obj, QueryFilm)
    assert saved_obj.query_id == query_id
    assert saved_obj.film_id == film_id
    assert saved_obj.similarity == similarity
    assert isinstance(saved_obj.similarity, Decimal)