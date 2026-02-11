"""Initial state

Revision ID: 9f883c173f3b
Revises: 
Create Date: 2025-11-24 10:38:01.972362

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '9f883c173f3b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
