"""v1_card_tags_rating_history

Revision ID: a7f3b2c91d04
Revises: dbb22ea86f29
Create Date: 2026-07-22

Adds:
- card_tags table for multi-tag support
- rating column to cards table
- card_history table for edit tracking
- flows table for debate flow data
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7f3b2c91d04"
down_revision: Union[str, Sequence[str], None] = "dbb22ea86f29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # card_tags table for multi-tag support
    op.create_table(
        "card_tags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("cards.id", ondelete="CASCADE")),
        sa.Column("tag_name", sa.String(), nullable=False),
    )
    op.create_index("ix_card_tags_card_id", "card_tags", ["card_id"])
    op.create_index("ix_card_tags_tag_name", "card_tags", ["tag_name"])

    # rating column on cards (1-5 stars, default 0 = unrated)
    op.add_column("cards", sa.Column("rating", sa.Integer(), server_default="0"))

    # card_history table for edit tracking
    op.create_table(
        "card_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("cards.id", ondelete="CASCADE")),
        sa.Column("field", sa.String(), nullable=False),
        sa.Column("old_value", sa.String()),
        sa.Column("new_value", sa.String()),
        sa.Column("changed_at", sa.String()),
    )
    op.create_index("ix_card_history_card_id", "card_history", ["card_id"])

    # flows table for debate flow data
    op.create_table(
        "flows",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("motion_id", sa.Integer(), sa.ForeignKey("motions.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("flow_data", sa.String()),  # JSON-encoded flow columns
        sa.Column("created_at", sa.String()),
        sa.Column("updated_at", sa.String()),
    )

    # export_log table for tracking exports
    op.create_table(
        "export_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("motion_id", sa.Integer()),
        sa.Column("format", sa.String()),
        sa.Column("filepath", sa.String()),
        sa.Column("card_count", sa.Integer()),
        sa.Column("exported_at", sa.String()),
    )


def downgrade() -> None:
    op.drop_table("export_log")
    op.drop_table("flows")
    op.drop_table("card_history")
    op.drop_column("cards", "rating")
    op.drop_index("ix_card_tags_tag_name")
    op.drop_index("ix_card_tags_card_id")
    op.drop_table("card_tags")
