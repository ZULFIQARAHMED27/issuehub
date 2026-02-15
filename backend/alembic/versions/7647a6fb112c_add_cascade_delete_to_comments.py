"""add cascade delete to comments

Revision ID: 7647a6fb112c
Revises: f0d86d4562c7
Create Date: 2026-02-13 19:39:20.423393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7647a6fb112c'
down_revision: Union[str, Sequence[str], None] = 'f0d86d4562c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = inspector.get_foreign_keys("comments")

    issue_fk = next(
        (fk for fk in foreign_keys if fk.get("constrained_columns") == ["issue_id"]),
        None
    )

    if issue_fk and issue_fk.get("options", {}).get("ondelete") != "CASCADE":
        op.drop_constraint(issue_fk["name"], "comments", type_="foreignkey")
        op.create_foreign_key(
            "comments_issue_id_fkey",
            "comments",
            "issues",
            ["issue_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = inspector.get_foreign_keys("comments")

    issue_fk = next(
        (fk for fk in foreign_keys if fk.get("constrained_columns") == ["issue_id"]),
        None
    )

    if issue_fk and issue_fk.get("options", {}).get("ondelete") == "CASCADE":
        op.drop_constraint(issue_fk["name"], "comments", type_="foreignkey")
        op.create_foreign_key(
            "comments_issue_id_fkey",
            "comments",
            "issues",
            ["issue_id"],
            ["id"],
        )
