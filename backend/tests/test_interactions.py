import pytest
from datetime import date
from app.models.client import Client
from app.models.film import Film
from app.schemas.interactions import InteractionType
from app.services.interactions_service import InteractionService

@pytest.fixture
def seed_data(db_session):
    client = Client(
        id=1,
        user_name="TestUser",
        email="test@example.com",
        password_hash="hashed_secret",
        date_of_birth=date(2000, 1, 1),
        is_active=True
    )

    film = Film(
        id=100,
        title="Test Movie",
        tmdb_id=12345
    )

    db_session.add(client)
    db_session.add(film)
    db_session.commit()
    return {"client_id": client.id, "film_id": film.id}


def test_create_interaction_click(db_session, seed_data):
    interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=seed_data["client_id"],
        film_id=seed_data["film_id"],
        action=InteractionType.CLICK
    )

    assert interaction.client_id == seed_data["client_id"]
    assert interaction.film_id == seed_data["film_id"]
    assert interaction.score == 1
    assert interaction.is_liked is False


def test_upsert_interaction_like(db_session, seed_data):
    InteractionService.register_interaction(
        db=db_session,
        client_id=seed_data["client_id"],
        film_id=seed_data["film_id"],
        action=InteractionType.CLICK
    )

    updated_interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=seed_data["client_id"],
        film_id=seed_data["film_id"],
        action=InteractionType.LIKE
    )

    assert updated_interaction.score == 10
    assert updated_interaction.is_liked is True


def test_watch_later_logic(db_session, seed_data):
    interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=seed_data["client_id"],
        film_id=seed_data["film_id"],
        action=InteractionType.WATCH_LATER
    )
    assert interaction.score == 5
    assert interaction.is_liked is False


def test_remove_like_logic(db_session, seed_data):
    InteractionService.register_interaction(
        db=db_session, client_id=seed_data["client_id"], film_id=seed_data["film_id"], action=InteractionType.LIKE
    )
    interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=seed_data["client_id"],
        film_id=seed_data["film_id"],
        action=InteractionType.REMOVE_LIKE
    )

    assert interaction.score == 5
    assert interaction.is_liked is False