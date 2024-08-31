from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Mapping, Set, Union
from unittest.mock import patch

import pytest
from pendulum.datetime import DateTime
from pendulum.tz.timezone import UTC
from sqlalchemy import select
from sqlalchemy.orm.session import Session as SASession

from duty_board import worker_duty_watcher
from duty_board.alchemy import update_duty_calendars
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from tests.conftest import get_loaded_ldap_plugin


@pytest.mark.usefixtures("_wipe_database")
def test_get_calendars_with_new_duty() -> None:
    # Ingest the calendars
    with get_loaded_ldap_plugin() as example_plugin:
        session: SASession
        with create_session() as session:
            update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
                session=session, duty_calendar_configurations=example_plugin.duty_calendar_configurations
            )

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
                start_event_utc=DateTime.utcnow() - timedelta(days=1),
                end_event_utc=DateTime.utcnow() + timedelta(days=1),
                calendar=calendars[0],
                person=persons[0],
            ),
            OnCallEvent(
                start_event_utc=DateTime.utcnow() + timedelta(days=1),
                end_event_utc=DateTime.utcnow() + timedelta(days=3),
                calendar=calendars[0],
                person=persons[1],
            ),
            OnCallEvent(
                start_event_utc=DateTime.utcnow() - timedelta(hours=1),
                end_event_utc=DateTime.utcnow() + timedelta(hours=1),
                calendar=calendars[1],
                person=persons[2],
            ),
        ]
        session.add_all(events)

    last_calendar_uid_to_person_id: Dict[str, Union[Set[int], None]] = defaultdict(lambda: None)
    with create_session() as session:
        # We verify the first run lists all the calendars.
        result = worker_duty_watcher.get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
        assert result == {
            "data_platform_duty": {persons[0].uid},
            "infrastructure_duty": {persons[2].uid},
            "machine_learning": set(),
        }

        # We verify in the second run that nothing actually changed.
        result = worker_duty_watcher.get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
        assert result == {}

    with create_session() as session:
        events[1].start_event_utc = DateTime.utcnow() - timedelta(days=1)
        session.merge(events[1])

    result = worker_duty_watcher.get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
    assert result == {"data_platform_duty": {persons[0].uid, persons[1].uid}}

    with create_session() as session:
        events[0].start_event_utc = DateTime.utcnow() + timedelta(hours=1)
        session.merge(events[0])

    result = worker_duty_watcher.get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
    assert result == {"data_platform_duty": {persons[1].uid}}

    with create_session() as session:
        events[1].start_event_utc = DateTime.utcnow() + timedelta(hours=1)
        session.merge(events[1])

    result = worker_duty_watcher.get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
    assert result == {"data_platform_duty": set()}


@pytest.mark.usefixtures("_wipe_database")
def test_run_update_event_loop() -> None:
    # Ingest the calendars
    with get_loaded_ldap_plugin() as example_plugin:
        session: SASession
        with create_session() as session:
            update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
                session=session, duty_calendar_configurations=example_plugin.duty_calendar_configurations
            )

    # Ingest the Persons & OnCallEvents
    with create_session() as session:
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

    with patch("duty_board.plugin.abstract_plugin.AbstractPlugin.handle_new_person_on_duty_event") as mocked:
        with create_session() as session:
            worker_duty_watcher.run_update_event_loop(
                session=session,
                plugin=example_plugin,
                calendars_with_new_on_call={
                    "data_platform_duty": {persons[0].uid, persons[1].uid},
                    "infrastructure_duty": {persons[2].uid},
                },
            )

        assert len(mocked.call_args_list) == 2
        call_args_list: Mapping[str, Any]
        call_args_list = mocked.call_args_list[0].kwargs
        kwarg_calendar: Calendar = call_args_list["calendar"]
        kwarg_persons: Set[Person] = call_args_list["persons"]

        assert kwarg_calendar.uid == "data_platform_duty"
        assert {person.uid for person in kwarg_persons} == {persons[0].uid, persons[1].uid}

        call_args_list = mocked.call_args_list[1].kwargs
        kwarg_calendar = call_args_list["calendar"]
        kwarg_persons = call_args_list["persons"]

        assert kwarg_calendar.uid == "infrastructure_duty"
        assert {person.uid for person in kwarg_persons} == {persons[2].uid}
