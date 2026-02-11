from unittest.mock import Mock, patch, MagicMock
from app.services.embedding_service import batch_encode, fetch_batch, insert_batch, connect_with_retry, \
    process_overviews, RETRY_LIMIT
from psycopg.errors import OperationalError


# Testing encoding function returns vectors
def test_batch_encode_returns_vectors():
    fake_texts = ["Hello", "World"]
    fake_model = MagicMock()
    fake_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]

    with patch("app.services.embedding_service.get_model", return_value=fake_model) as mock_get_model:
        vectors = batch_encode(fake_texts)

        mock_get_model.assert_called_once()
        fake_model.encode.assert_called_once_with(fake_texts, batch_size=32)
        assert vectors == [[0.1, 0.2], [0.3, 0.4]]


# Testing fetching function on returning mocked rows
def test_fetch_batch():
    mock_conn = MagicMock()

    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, "overview 1"),
        (2, "overview 2"),
    ]

    rows = fetch_batch(mock_conn)

    assert len(rows) == 2


# Testing insertion function with mocked rows
def test_insert_batch_executes_queries():
    mock_conn = MagicMock()

    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    batch_rows = [
        (1, [0.1, 0.2, 0.3]),
        (2, [0.4, 0.5, 0.6])
    ]

    insert_batch(mock_conn, batch_rows)

    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()


# Testing reconnection to db
def test_connect_with_retry_retries_on_failure():
    with patch("app.services.embedding_service.ps.connect") as mock_connect:

        mock_connect.side_effect = [OperationalError("lost"), Mock()]
        conn = connect_with_retry()
        assert conn is not None
        assert mock_connect.call_count == 2


# Testing fail after 3 attempts of reconnection
def test_connect_with_retry_fails_after_retries():
    with patch("app.services.embedding_service.ps.connect", side_effect=OperationalError("fail")), \
         patch("app.services.embedding_service.time.sleep") as mock_sleep:

        try:
            connect_with_retry()
            assert False, "Expected RuntimeError"
        except RuntimeError:
            pass

        # RETRY_LIMIT = 3 → 3 attempts
        assert mock_sleep.call_count == 3


# Testing a main function that performs the whole process of ETL system
def test_process_overviews_retries():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("app.services.embedding_service.connect_with_retry", return_value=mock_conn), \
         patch("app.services.embedding_service.fetch_batch", side_effect=[[(1, "text1")], []]), \
         patch("app.services.embedding_service.batch_encode", return_value=[[0.1, 0.2, 0.3]]), \
         patch("app.services.embedding_service.insert_batch") as mock_insert:

        process_overviews()

        mock_insert.assert_called_once()


# Testing reconnection after fetch fail in a main function
def test_process_overviews_fetch_error_triggers_reconnect():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fake_model = MagicMock()
    fake_model.encode.return_value = []

    with patch("app.services.embedding_service.connect_with_retry", side_effect=[mock_conn, mock_conn]) as mock_conn_retry, \
         patch("app.services.embedding_service.fetch_batch", side_effect=[OperationalError("lost"), []]), \
         patch("app.services.embedding_service.get_model", return_value=fake_model):

        process_overviews()

        assert mock_conn_retry.call_count == 2



# Testing insert_batch throws an Exception, function throws sleep and reconnects
def test_process_overviews_insert_generic_exception_retry():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fake_model = MagicMock()
    fake_model.encode.return_value = [[0.1, 0.2]]

    with patch("app.services.embedding_service.connect_with_retry", return_value=mock_conn), \
         patch("app.services.embedding_service.fetch_batch", side_effect=[[(1, "text")], []]), \
         patch("app.services.embedding_service.get_model", return_value=fake_model), \
         patch("app.services.embedding_service.insert_batch", side_effect=[Exception("fail"), None]) as mock_insert, \
         patch("app.services.embedding_service.time.sleep") as mock_sleep:

        process_overviews()

        assert mock_insert.call_count == 2
        assert mock_sleep.called



# Testing first insert_batch failing but retry still working
def test_process_overviews_insert_retries_on_operational_error():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fake_model = MagicMock()
    fake_model.encode.return_value = [[0.1, 0.2]]

    with patch("app.services.embedding_service.connect_with_retry", return_value=mock_conn), \
         patch("app.services.embedding_service.fetch_batch", side_effect=[[(1, "text")], []]), \
         patch("app.services.embedding_service.get_model", return_value=fake_model), \
         patch("app.services.embedding_service.insert_batch", side_effect=[OperationalError("lost"), None]) as mock_insert:

        process_overviews()

        assert mock_insert.call_count == 2


# Testing case where fetch_batch returns an empty list -> process_overviews does nothing
def test_process_overviews_immediate_empty_batch():
    mock_conn = MagicMock()

    with patch("app.services.embedding_service.connect_with_retry", return_value=mock_conn), \
        patch("app.services.embedding_service.fetch_batch", return_value=[]):

        process_overviews()

        mock_conn.close.assert_called_once()


# Testing main function going through whole process and calling conn.close
def test_process_overviews_closes_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fake_model = MagicMock()
    fake_model.encode.return_value = [[0.1]]

    with patch("app.services.embedding_service.connect_with_retry", return_value=mock_conn), \
         patch("app.services.embedding_service.fetch_batch", side_effect=[[(1, "text")], []]), \
         patch("app.services.embedding_service.get_model", return_value=fake_model), \
         patch("app.services.embedding_service.insert_batch", return_value=None):

        process_overviews()

        mock_conn.close.assert_called_once()



# Testing connecting to database with conn being None
def test_connect_with_retry_fails_without_url():
    with patch("app.services.embedding_service.DATABASE_URL", None), \
         patch("app.services.embedding_service.ps.connect", side_effect=OperationalError("invalid URL")), \
         patch("app.services.embedding_service.time.sleep") as mock_sleep:

        try:
            connect_with_retry()
            assert False, "Expected RuntimeError"
        except RuntimeError:
            pass

        assert mock_sleep.call_count == RETRY_LIMIT


# Testing query used for fetching data
def test_fetch_batch_executes_correct_query():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    fetch_batch(mock_conn)

    executed_query = mock_cursor.execute.call_args[0][0]
    assert "SELECT id, overview" in executed_query
    assert "FROM film" in executed_query
    assert "NOT IN (SELECT film_id FROM vectors)" in executed_query


# Testing fetch_batch returning empty list
def test_fetch_batch_returns_empty_list():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    rows = fetch_batch(mock_conn)
    assert rows == []


# Testing if commit is called
def test_insert_batch_commits_after_insert():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    insert_batch(mock_conn, [(1, [0.1, 0.2])])
    mock_conn.commit.assert_called_once()


# Testing insert_batch inserting nothing if rows = []
def test_insert_batch_empty_input():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    insert_batch(mock_conn, [])

    mock_cursor.execute.assert_not_called()
    mock_conn.commit.assert_called_once()


# Testing batch_encode returning [] if given empty list
def test_batch_encode_empty_list():
    fake_model = MagicMock()
    fake_model.encode.return_value = []

    with patch("app.services.embedding_service.get_model", return_value=fake_model) as mock_get_model:
        result = batch_encode([])

        mock_get_model.assert_called_once()
        fake_model.encode.assert_called_once_with([], batch_size=32)
        assert result == []

