from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.client_interaction import ClientInteraction
from app.schemas.interactions import InteractionType


class InteractionService:
    @staticmethod
    def calculate_score_and_status(action: InteractionType) -> tuple[int, bool]:

        if action == InteractionType.LIKE:
            return 10, True
        elif action == InteractionType.WATCH_LATER:
            return 5, False
        elif action == InteractionType.CLICK:
            return 1, False
        elif action == InteractionType.REMOVE_LIKE:
            return 5, False
        elif action == InteractionType.REMOVE_WATCH_LATER:
            return 1, False
        return 1, False

    @classmethod
    def register_interaction(
            cls,
            db: Session,
            client_id: int,
            film_id: int,
            action: InteractionType
    ) -> ClientInteraction:

        new_score, new_is_liked = cls.calculate_score_and_status(action)

        query = select(ClientInteraction).where(
            ClientInteraction.client_id == client_id,
            ClientInteraction.film_id == film_id
        )
        interaction = db.scalar(query)

        if interaction:
            interaction.score = new_score
            interaction.is_liked = new_is_liked
        else:
            interaction = ClientInteraction(
                client_id=client_id,
                film_id=film_id,
                score=new_score,
                is_liked=new_is_liked
            )
            db.add(interaction)

        db.commit()
        db.refresh(interaction)
        return interaction