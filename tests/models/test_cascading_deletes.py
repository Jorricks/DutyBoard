# Note: the cascading delete on Calendar.events has already been tested by `tests/alchemy/test_update_duty_calendars.py`
from typing import List

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.person import Person
from duty_board.models.person_image import PersonImage


def test_person_image_delete(set_up_persons: List[Person]) -> None:
    session: SASession
    with create_session() as session:
        assert len(session.scalars(select(PersonImage)).all()) == 2
        stmt = delete(PersonImage).where(PersonImage.uid == set_up_persons[0].image_uid)
        with pytest.raises(IntegrityError, match='violates foreign key constraint "person_image_uid_fkey"'):
            session.execute(stmt)

    with create_session() as session:
        assert len(session.scalars(select(PersonImage)).all()) == 2
