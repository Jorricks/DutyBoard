"""Add field to contain extra information of a Calendar

Revision ID: 2e1f3badfabe
Revises: 9af1232f6bc0
Create Date: 2024-08-31 12:20:01.752969

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e1f3badfabe"
down_revision: Union[str, None] = "9af1232f6bc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("calendar", sa.Column("extra_info", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("calendar", "extra_info")
