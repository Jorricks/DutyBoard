from datetime import datetime, timedelta
from typing import List

import pytest
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC
from sqlalchemy import select
from sqlalchemy.orm.session import Session as SASession

from duty_board import worker_duty_officer
from duty_board.alchemy import update_duty_calendars
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from tests.conftest import get_loaded_ldap_plugin


@pytest.mark.usefixtures("_wipe_database")
def test_update_the_most_outdated_person() -> None:
    # Ingest the calendars
    with get_loaded_ldap_plugin() as example_plugin:
        session: SASession
        with create_session() as session:
            update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
                session=session, duty_calendar_configurations=example_plugin.duty_calendar_configurations
            )
        # First run is when there is nothing to update yet :)
        worker_duty_officer.update_the_most_outdated_person(example_plugin)

    # Ingest the Persons & OnCallEvents
    with create_session() as session:
        calendars: List[Calendar] = list(session.scalars(select(Calendar)).all())
        persons: List[Person] = [
            Person(
                username="jan",
                email=None,
                last_update_utc=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
            ),
            Person(
                username=None,
                email="henk@tank.nl",
                last_update_utc=datetime(1970, 1, 1, 0, 0, 1, tzinfo=UTC),
            ),
            Person(
                username="henk",
                email=None,
                last_update_utc=datetime(1970, 1, 1, 0, 0, 2, tzinfo=UTC),
            ),
        ]
        session.add_all(persons)
        events: List[OnCallEvent] = [
            OnCallEvent(
                start_event_utc=DateTime.utcnow() + timedelta(days=1),
                end_event_utc=DateTime.utcnow() + timedelta(days=2),
                calendar=calendars[0],
                person=persons[0],
            ),
            OnCallEvent(
                start_event_utc=DateTime.utcnow() + timedelta(days=2),
                end_event_utc=DateTime.utcnow() + timedelta(days=3),
                calendar=calendars[0],
                person=persons[1],
            ),
            OnCallEvent(
                start_event_utc=DateTime.utcnow() + timedelta(days=3),
                end_event_utc=DateTime.utcnow() + timedelta(days=4),
                calendar=calendars[0],
                person=persons[2],
            ),
        ]
        session.add_all(events)

    # We verify the events have different persons linked to them
    with create_session() as session:
        on_call_events = list(session.scalars(select(OnCallEvent).order_by(OnCallEvent.start_event_utc)).all())
        assert on_call_events[1].person_uid != on_call_events[2].person_uid

    # We proceed to do our three runs to update all three persons
    with get_loaded_ldap_plugin() as example_plugin:
        worker_duty_officer.update_the_most_outdated_person(example_plugin)
        worker_duty_officer.update_the_most_outdated_person(example_plugin)
        worker_duty_officer.update_the_most_outdated_person(example_plugin)

    # Here we verify that the users were filled in and user 1 and 2 were combined.
    with create_session() as session:
        persons = list(session.scalars(select(Person)).all())
        assert len(persons) == 2
        assert persons[0].email == "jan@schoenmaker.nl"
        assert persons[1].email == "henk@tank.nl"

        on_call_events = list(session.scalars(select(OnCallEvent).order_by(OnCallEvent.start_event_utc)).all())
        assert on_call_events[1].person_uid == on_call_events[2].person_uid
