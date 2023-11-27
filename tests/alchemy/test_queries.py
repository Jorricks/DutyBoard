import os

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker
from tzlocal import get_localzone

from duty_board.alchemy import queries
from duty_board.models import generate_fake_data
from duty_board.models.person import Person

engine = create_engine(os.environ["SQL_ALCHEMY_CONNECTION"])
Session = sessionmaker(engine)


def _create_fake_data(session: SASession) -> None:
    generate_fake_data.create_fake_database_rows_if_not_present(session)


def test_get_calendars() -> None:
    with Session.begin() as session:
        _create_fake_data(session)
        person_uids = [person.uid for person in session.scalars(select(Person)).all()]
        queries.get_calendars(
            session=session,
            all_encountered_person_uids=set(person_uids),
            timezone=get_localzone(),
        )
