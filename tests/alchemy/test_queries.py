from sqlalchemy import select
from sqlalchemy.orm import Session as SASession
from tzlocal import get_localzone

from duty_board.alchemy import queries
from duty_board.alchemy.session import create_session
from duty_board.models import generate_fake_data
from duty_board.models.person import Person


def _create_fake_data(session: SASession) -> None:
    generate_fake_data.create_fake_database_rows_if_not_present(session)


def test_get_calendars() -> None:
    with create_session() as session:
        _create_fake_data(session)
        person_uids = [person.uid for person in session.scalars(select(Person)).all()]
        queries.get_calendars(
            session=session,
            all_encountered_person_uids=set(person_uids),
            timezone=get_localzone(),
        )


# @ToDo(jorrick)
