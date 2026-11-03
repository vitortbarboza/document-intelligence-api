"""enable sqlite autoincrement

Revision ID: 47d1a5b7719a
Revises: 691574a44504
Create Date: 2026-10-30 15:52:46.824301

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "47d1a5b7719a"
down_revision: str | Sequence[str] | None = "691574a44504"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable explicit SQLite AUTOINCREMENT for document IDs."""
    with op.batch_alter_table(
        "documents",
        recreate="always",
        table_kwargs={"sqlite_autoincrement": True},
    ):
        pass


def downgrade() -> None:
    """Restore SQLite's default integer primary key behavior."""
    with op.batch_alter_table(
        "documents",
        recreate="always",
        table_kwargs={"sqlite_autoincrement": False},
    ):
        pass
