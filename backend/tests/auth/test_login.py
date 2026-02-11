# tests/test_login.py
from datetime import date, datetime
from app.services.auth.login_service import LoginService
from app.models.client import Client
from app.models.client_session import ClientSession
from app.utils.security import hash_password
from app.schemas.auth.login import LoginRequest

def test_login_success(db_session):
    password = "Password123"
    hashed = hash_password(password)

    client = Client(
        user_name="dan_login",
        email="dan@example.com",
        password_hash=hashed,
        is_active=True,
        confirmed_email=True,
        date_of_birth=date(1990, 1, 1)
    )
    db_session.add(client)
    db_session.commit()

    service = LoginService(db_session)
    login_data = LoginRequest(email="dan@example.com", password=password)
    response = service.login(login_data)

    assert response.session_token is not None
    assert response.expires_at > datetime.utcnow()

    session = db_session.query(ClientSession).filter_by(client_id=client.id).first()
    assert session is not None
    assert session.session_token == response.session_token