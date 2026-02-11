import pytest

from app.schemas.interactions import InteractionType
from app.services.interactions_service import InteractionService


def test_interaction_click(db_session):
    interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=1,
        film_id=100,
        action=InteractionType.CLICK
    )

    assert interaction.score == 1
    assert interaction.is_liked is False
    assert interaction.client_id == 1
    assert interaction.film_id == 100


def test_interaction_like(db_session):
    interaction = InteractionService.register_interaction(
        db=db_session,
        client_id=1,
        film_id=100,
        action=InteractionType.LIKE
    )

    assert interaction.score == 10
    assert interaction.is_liked is True


def test_interaction_update_flow(db_session):
    InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.CLICK
    )

    inter_liked = InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.LIKE
    )
    assert inter_liked.score == 10
    assert inter_liked.is_liked is True

    inter_deliked = InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.REMOVE_LIKE
    )
    assert inter_deliked.score == 5
    assert inter_deliked.is_liked is False


def test_watch_later_logic(db_session):
    interaction = InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.WATCH_LATER
    )
    assert interaction.score == 5
    assert interaction.is_liked is False


def test_remove_watch_later(db_session):
    InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.WATCH_LATER
    )
    result = InteractionService.register_interaction(
        db=db_session, client_id=1, film_id=100, action=InteractionType.REMOVE_WATCH_LATER
    )
    assert result.score == 1