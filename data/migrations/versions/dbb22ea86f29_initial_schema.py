"""initial_schema

Revision ID: dbb22ea86f29
Revises:
Create Date: 2026-05-12 16:57:59.633606

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dbb22ea86f29"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # motions table
    op.create_table(
        "motions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_archived", sa.Boolean(), server_default="0"),
    )
    # cards table
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("motion_id", sa.Integer(), sa.ForeignKey("motions.id")),
        sa.Column("tag", sa.String()),
        sa.Column("citation", sa.String()),
        sa.Column("side", sa.String()),
        sa.Column("text", sa.String()),
        sa.Column("language", sa.String()),
        sa.Column("mastery", sa.Integer(), server_default="0"),
        sa.Column("tier", sa.Integer(), server_default="1"),
        sa.Column("timestamp", sa.String()),
    )
    # trash table
    op.create_table(
        "trash",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("motion_id", sa.Integer()),
        sa.Column("card_json", sa.String()),
        sa.Column("deleted_at", sa.String()),
    )
    # metadata table
    op.create_table(
        "metadata",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("value", sa.String()),
    )

    # FTS5 and Triggers (Direct SQL)
    op.execute(
        "CREATE VIRTUAL TABLE cards_fts USING fts5(tag, citation, text, content='cards', content_rowid='id')"
    )
    op.execute("""
        CREATE TRIGGER cards_ai AFTER INSERT ON cards BEGIN
            INSERT INTO cards_fts(rowid, tag, citation, text) VALUES (new.id, new.tag, new.citation, new.text);
        END
    """)
    op.execute("""
        CREATE TRIGGER cards_ad AFTER DELETE ON cards BEGIN
            INSERT INTO cards_fts(cards_fts, rowid, tag, citation, text) VALUES('delete', old.id, old.tag, old.citation, old.text);
        END
    """)
    op.execute("""
        CREATE TRIGGER cards_au AFTER UPDATE ON cards BEGIN
            INSERT INTO cards_fts(cards_fts, rowid, tag, citation, text) VALUES('delete', old.id, old.tag, old.citation, old.text);
            INSERT INTO cards_fts(rowid, tag, citation, text) VALUES (new.id, new.tag, new.citation, new.text);
        END
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS cards_au")
    op.execute("DROP TRIGGER IF EXISTS cards_ad")
    op.execute("DROP TRIGGER IF EXISTS cards_ai")
    op.execute("DROP TABLE IF EXISTS cards_fts")
    op.drop_table("metadata")
    op.drop_table("trash")
    op.drop_table("cards")
    op.drop_table("motions")
