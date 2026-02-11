import pytest
from app.services.history_service import (
    delete_all_queries,
    get_user_history_with_films,
    delete_selected_query
)
from app.models import UserQuery


def test_delete_all_queries_success(mocker):
    mock_db = mocker.Mock()
    client_id = 1

    mock_result = mocker.Mock()
    mock_result.scalars.return_value.all.return_value = [10, 11, 12]
    mock_db.execute.return_value = mock_result

    deleted_count = delete_all_queries(db=mock_db, client_id=client_id)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    assert deleted_count == 3


def test_get_user_history_with_films_success(mocker):
    mock_db = mocker.Mock()
    user_id = 1

    mock_query_obj = mocker.Mock(spec=UserQuery)
    mock_query_obj.id = 100
    mock_query_obj.client_id = user_id

    mock_result = mocker.Mock()
    mock_result.all.return_value = [mock_query_obj]
    mock_db.scalars.return_value = mock_result

    result = get_user_history_with_films(db=mock_db, user_id=user_id)

    mock_db.scalars.assert_called_once()
    assert len(result) == 1
    assert result[0].id == 100
    assert result[0].client_id == user_id


def test_delete_selected_query_success(mocker):
    mock_db = mocker.Mock()
    query_id = 5
    client_id = 1

    mock_result = mocker.Mock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    result = delete_selected_query(db=mock_db, query_id=query_id, client_id=client_id)

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    assert result is True


def test_delete_selected_query_not_found(mocker):
    mock_db = mocker.Mock()
    query_id = 999
    client_id = 1

    mock_result = mocker.Mock()
    mock_result.rowcount = 0
    mock_db.execute.return_value = mock_result

    result = delete_selected_query(db=mock_db, query_id=query_id, client_id=client_id)

    mock_db.commit.assert_called_once()
    assert result is False