from dataclasses import dataclass
from datetime import date

from app.main import app
from app.utils.dependencies import get_current_client


@dataclass
class FakeClient:
    id: int
    user_name: str
    email: str
    date_of_birth: date | None


def test_profile_me_requires_auth(client):
    # Без override буде реальна HTTPBearer перевірка -> має дати 403 "Not authenticated"
    r = client.get("/profile/me")
    assert r.status_code in (401, 403)


def test_profile_me_returns_profile_with_aliases(client):
    fake = FakeClient(
        id=1,
        user_name="yurii",
        email="yurii@example.com",
        date_of_birth=date(2006, 1, 15),
    )

    def override_get_current_client():
        return fake

    app.dependency_overrides[get_current_client] = override_get_current_client
    try:
        r = client.get("/profile/me", headers={"Authorization": "Bearer test"})
        assert r.status_code == 200

        data = r.json()
        # Важливо: ми очікуємо саме поля, які фронт хоче
        assert data["username"] == "yurii"
        assert data["email"] == "yurii@example.com"
        assert data["birth_date"] == "2006-01-15"

        # І переконуємось, що внутрішні назви НЕ витекли
        assert "user_name" not in data
        assert "date_of_birth" not in data
    finally:
        app.dependency_overrides.clear()


def test_profile_me_birth_date_can_be_null(client):
    fake = FakeClient(
        id=2,
        user_name="no-bday",
        email="nobday@example.com",
        date_of_birth=None,
    )

    def override_get_current_client():
        return fake

    app.dependency_overrides[get_current_client] = override_get_current_client
    try:
        r = client.get("/profile/me", headers={"Authorization": "Bearer test"})
        assert r.status_code == 200
        data = r.json()
        assert data["birth_date"] is None
    finally:
        app.dependency_overrides.clear()
