from unittest.mock import MagicMock
import pytest
from scripts.init_db import init_db

def test_init_db_creates_tables(mocker):
    mock_create_all = mocker.patch("scripts.init_db.BaseModel.metadata.create_all")

    mock_engine = MagicMock()
    mocker.patch("scripts.init_db.engine", mock_engine)

    init_db()

    mock_create_all.assert_called_once_with(bind=mock_engine)

def test_init_db_create_all_failure(mocker, capsys):
    mocker.patch("scripts.init_db.BaseModel.metadata.create_all", side_effect=Exception("DB Error"))

    mock_engine = MagicMock()
    mocker.patch("scripts.init_db.engine", mock_engine)

    with pytest.raises(SystemExit) as exc_info:
        init_db()

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Помилка при створенні БД: DB Error" in captured.out