# tests/test_auth_routes.py
from datetime import date


def test_register_endpoint(client):
    data = {
        "user_name": "eve_test",
        "email": "eve@example.com",
        "password": "Password123",
        "date_of_birth": "1992-05-20"
    }

    response = client.post("/auth/register", json=data)

    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["user_name"] == "eve_test"
    assert body["email"] == "eve@example.com"


def test_login_endpoint(client, db_session):
    from app.utils.security import hash_password
    from app.models.client import Client

    password = "Password123"

    client_db = Client(
        user_name="frank_test",
        email="frank@example.com",
        password_hash=hash_password(password),
        is_active=True,
        confirmed_email=True,
        date_of_birth=date(1992, 5, 20)
    )

    db_session.add(client_db)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "frank@example.com",
            "password": password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data