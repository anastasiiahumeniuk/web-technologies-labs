from dotenv import load_dotenv
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.getcwd())
load_dotenv()

R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL")
R2_BUCKET = os.getenv("R2_BUCKET_NAME")

from app.services.cloud_service import get_s3_client, upload_file_to_r2

def test_get_s3_client_success(monkeypatch):
    monkeypatch.setenv('R2_ACCESS_KEY_ID', "abc")
    monkeypatch.setenv('R2_SECRET_ACCESS_KEY', "xyz")
    monkeypatch.setenv('R2_ENDPOINT_URL', "http://example.com")
    monkeypatch.setenv('R2_BUCKET_NAME', "bucket")

    with patch("boto3.client") as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance

        client = get_s3_client()
        assert client is instance
        mock_client.assert_called_once()

def test_get_s3_client_no_keys_failure(monkeypatch):
    monkeypatch.delenv("R2_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("R2_SECRET_ACCESS_KEY", raising=False)

    client = get_s3_client()
    assert client is None

def test_upload_file_to_r2_no_key(monkeypatch):
    monkeypatch.delenv('R2_ACCESS_KEY_ID', raising=False)
    monkeypatch.delenv('R2_SECRET_ACCESS_KEY', raising=False)
    monkeypatch.delenv('R2_ENDPOINT_URL', raising=False)
    monkeypatch.delenv('R2_BUCKET_NAME', raising=False)

    client3 = get_s3_client()

    assert client3 is None

    result = upload_file_to_r2(b"dummy data", "dummy_key.jpg")
    assert result is None

def test_upload_file_to_r2_key_available(monkeypatch):

    monkeypatch.setenv('R2_ACCESS_KEY_ID', "abc")
    monkeypatch.setenv('R2_SECRET_ACCESS_KEY', "xyz")
    monkeypatch.setenv('R2_ENDPOINT_URL', "http://example.com")
    monkeypatch.setenv('R2_BUCKET_NAME', "bucket")

    with patch("boto3.client") as mock_client:
        fake_client = MagicMock()
        mock_client.return_value = fake_client

        client = get_s3_client()
        assert client is fake_client

        mock_client.assert_called_once_with(
            's3',
            endpoint_url='http://example.com',
            aws_access_key_id='abc',
            aws_secret_access_key='xyz',
            region_name='auto',
        )

def test_upload_file_to_r2_no_client(monkeypatch):
    with patch("app.services.cloud_service.get_s3_client", return_value=None):
        result = upload_file_to_r2(b"data", "file.jpg")
        assert result is None

def test_upload_file_to_r2_client_available(monkeypatch):
    fake_client = MagicMock()
    fake_client.put_object.return_value = {}
    with patch("app.services.cloud_service.get_s3_client", return_value=fake_client):
        key = upload_file_to_r2(b"data", "file.jpg")
        assert key == 'file.jpg'
        fake_client.put_object.assert_called_once()

def test_upload_file_to_r2_put_object_exception(monkeypatch):
    fake_client = MagicMock()
    fake_client.put_object.side_effect = Exception("Fail")
    with patch("app.services.cloud_service.get_s3_client", return_value=fake_client):
        result = upload_file_to_r2(b"data", "file.jpg")
        assert result is None