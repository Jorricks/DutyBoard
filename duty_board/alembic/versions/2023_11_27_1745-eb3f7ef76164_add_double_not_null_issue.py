"""add double_not_null issue

Revision ID: eb3f7ef76164
Revises: e16bfce2c936
Create Date: 2023-11-27 17:45:40.380756

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eb3f7ef76164"
down_revision: Union[str, None] = "e16bfce2c936"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("on_call_event__uid", "on_call_event", ["uid"])
    op.drop_constraint("person_email_key", "person", type_="unique")
    op.drop_constraint("person_username_key", "person", type_="unique")
    op.create_unique_constraint("person__uid", "person", ["uid"])
    op.create_unique_constraint("person_image__uid", "person_image", ["uid"])
    op.create_unique_constraint("token__token", "token", ["token"])
    # ### end Alembic commands ###
    op.create_check_constraint("person_double_null", "person", "NOT(username IS NULL AND email IS NULL)")


def downgrade() -> None:
    op.drop_constraint("person_double_null", "person", type_="check")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("token__token", "token", type_="unique")
    op.drop_constraint("person_image__uid", "person_image", type_="unique")
    op.drop_constraint("person__uid", "person", type_="unique")
    op.create_unique_constraint("person_username_key", "person", ["username"])
    op.create_unique_constraint("person_email_key", "person", ["email"])
    op.drop_constraint("on_call_event__uid", "on_call_event", type_="unique")
    # ### end Alembic commands ###
