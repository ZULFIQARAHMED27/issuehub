"""add start_date to projects

Revision ID: 2a4c6d8e9f10
Revises: 7647a6fb112c
Create Date: 2026-02-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2a4c6d8e9f10"
down_revision: Union[str, Sequence[str], None] = "7647a6fb112c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("projects", sa.Column("start_date", sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "start_date")
