"""Add initial tables

Revision ID: 25f00fd34f6a
Revises:
Create Date: 2023-11-19 13:41:45.501417

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from duty_board.alchemy.sqlalchemy_types import UtcDateTime

# revision identifiers, used by Alembic.
revision: str = "25f00fd34f6a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "calendar",
        sa.Column("uid", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("icalendar_url", sa.String(length=500), nullable=True),
        sa.Column("event_prefix", sa.String(length=50), nullable=True),
        sa.Column(
            "error_msg",
            sa.String(length=9999),
            nullable=True,
            comment="If any, the error of the latest sync attempt.",
        ),
        sa.Column("last_update_utc", UtcDateTime(timezone=True), nullable=False),
        sa.Column("sync", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uid"),
    )
    op.create_index("calendar_last_update_utc", "calendar", ["last_update_utc"], unique=False)

    op.create_table(
        "person",
        sa.Column("uid", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=50), nullable=True),
        sa.Column("img_filename", sa.String(length=100), nullable=True),
        sa.Column("img_width", sa.Integer(), nullable=True),
        sa.Column("img_height", sa.Integer(), nullable=True),
        sa.Column(
            "extra_attributes_json",
            sa.String(length=100000),
            nullable=True,
            comment="Extra attributes represented as a json.",
        ),
        sa.Column(
            "error_msg",
            sa.String(length=9999),
            nullable=True,
            comment="If any, the error of the latest sync attempt.",
        ),
        sa.Column("last_update_utc", UtcDateTime(timezone=True), nullable=False),
        sa.Column("sync", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uid"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("uid"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("person_last_update_utc", "person", ["last_update_utc"], unique=False)

    op.create_table(
        "on_call_event",
        sa.Column("uid", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("calendar_uid", sa.String(length=50), nullable=False),
        sa.Column("start_event_utc", UtcDateTime(timezone=True), nullable=False),
        sa.Column("end_event_utc", UtcDateTime(timezone=True), nullable=False),
        sa.Column("person_uid", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(("calendar_uid",), ["calendar.uid"]),
        sa.ForeignKeyConstraint(("person_uid",), ["person.uid"]),
        sa.PrimaryKeyConstraint("uid"),
        sa.UniqueConstraint("uid"),
    )

    op.create_table(
        "token",
        sa.Column("token", sa.String(length=50), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("last_update_utc", UtcDateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("token"),
        sa.UniqueConstraint("token"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("token_last_update_utc", "token", ["last_update_utc"], unique=False)


def downgrade() -> None:
    op.drop_table("on_call_event")
    op.drop_index("token_last_update_utc", table_name="token")
    op.drop_table("token")
    op.drop_index("person_last_update_utc", table_name="person")
    op.drop_table("person")
    op.drop_index("calendar_last_update_utc", table_name="calendar")
    op.drop_table("calendar")
