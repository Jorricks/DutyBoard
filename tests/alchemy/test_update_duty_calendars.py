from datetime import timedelta
from typing import List

from pendulum import DateTime
from sqlalchemy import delete, select
from sqlalchemy.orm.session import Session as SASession

from duty_board.alchemy import update_duty_calendars
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.plugin.abstract_plugin import AbstractPlugin
from tests.conftest import get_loaded_ldap_plugin

# @ToDo(jorrick) make sure to test for the foreignkey issue


def test_sync_duty_calendar_configurations_to_postgres(set_up_persons: List[Person]) -> None:
    session: SASession
    example_plugin: AbstractPlugin
    # Do the standard first sync
    with create_session() as session, get_loaded_ldap_plugin() as example_plugin:
        update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
            session=session, duty_calendar_configurations=example_plugin.duty_calendar_configurations
        )

    # We verify the sync was successful
    with create_session() as session:
        all_calendars: List[Calendar] = list(session.scalars(select(Calendar)).all())
        assert len(all_calendars) == 3
        assert set(c.uid for c in all_calendars) == {"data_platform_duty", "infrastructure_duty", "machine_learning"}
        assert len(list(session.scalars(select(Person)).all())) == 2

    # Now we add some events.
    with create_session() as session:
        all_calendars = list(session.scalars(select(Calendar)).all())
        assert len(all_calendars) == 3
        persons = list(session.scalars(select(Person)).all())
        assert len(persons) == 2
        for calendar in all_calendars:
            calendar.events = [
                OnCallEvent(
                    start_event_utc=DateTime.utcnow(),
                    end_event_utc=DateTime.utcnow() + timedelta(days=1),
                    calendar=calendar,
                    person=persons[0],
                ),
                OnCallEvent(
                    start_event_utc=DateTime.utcnow() + timedelta(days=1),
                    end_event_utc=DateTime.utcnow() + timedelta(days=2),
                    calendar=calendar,
                    person=persons[1],
                ),
            ]

    # We verify the events are there
    with create_session() as session:
        all_calendars = list(session.scalars(select(Calendar)).all())
        for calendar in all_calendars:
            assert len(calendar.events) == 2
            assert calendar.events[0].person.username == "jan"
            assert calendar.events[1].person.username == "henk"
        assert len(list(session.scalars(select(OnCallEvent)))) == 3 * 2  # 3 calendars, 2 events per calendar

    # Now we do another sync with a subset of the items and slightly renamed.
    with create_session() as session:
        modified_calendar = example_plugin.duty_calendar_configurations[1]
        modified_calendar.uid = "infrastructure_duty_refreshed"
        update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
            session=session,
            duty_calendar_configurations=[example_plugin.duty_calendar_configurations[0], modified_calendar],
        )

    # Now we verify that the events were deleted, persons were kept, and calendars table was updated as expected.
    with create_session() as session:
        all_calendars: List[Calendar] = list(session.scalars(select(Calendar)).all())
        assert len(all_calendars) == 2
        assert set(c.uid for c in all_calendars) == {"data_platform_duty", "infrastructure_duty_refreshed"}
        assert len(list(session.scalars(select(Person)).all())) == 2
        assert len(list(session.scalars(select(OnCallEvent)))) == 2

    # Now we verify that if we delete one of the two persons, it automatically keeps only one OnCallEvent.
    with create_session() as session:
        persons = list(session.scalars(select(Person)).all())
        assert len(persons) == 2
        session.execute(delete(Person).where(Person.uid == persons[0].uid))

    with create_session() as session:
        persons = list(session.scalars(select(Person)).all())
        assert len(persons) == 1
        assert len(list(session.scalars(select(OnCallEvent)))) == 1
