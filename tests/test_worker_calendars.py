from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import pytest
import requests_mock
from pendulum.tz.timezone import UTC
from sqlalchemy import select
from sqlalchemy.orm.session import Session as SASession

from duty_board import worker_calendars
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from tests import ical_helper
from tests.conftest import get_loaded_ldap_plugin


@pytest.mark.usefixtures("_wipe_database")
def test_update_the_most_outdated_calendar() -> None:
    # First run is when there is nothing to update yet :)
    with get_loaded_ldap_plugin() as example_plugin:
        worker_calendars.update_the_most_outdated_calendar(example_plugin)

    # Create the calendar
    session: SASession
    with create_session() as session:
        calendar = Calendar(
            uid="data_platform_duty",
            name="Data Platform Duty",
            description="Call us for your issues with the data platform",
            icalendar_url="https://non-existing-url.com/icalendar.ics",
            category="Big Data",
            order=1,
            last_update_utc=datetime(1970, 1, 1, 0, 0, 2, tzinfo=UTC),
            sync=False,
        )
        session.add(calendar)

    # Do the actual update loop
    with get_loaded_ldap_plugin() as example_plugin, requests_mock.Mocker() as m:
        events: List[Tuple[Optional[str], Optional[str], timedelta, timedelta]] = [
            ("jan", None, timedelta(days=0), timedelta(days=1)),
            ("jan", "mailto:jan@schoenmaker.nl", timedelta(days=1), timedelta(days=1)),
            ("henkietankie", "henk@tank.nl", timedelta(days=2), timedelta(days=20)),
        ]
        ical_response = ical_helper.get_icalendar_response(events=events)
        m.get("https://non-existing-url.com/icalendar.ics", text=ical_response)

        worker_calendars.update_the_most_outdated_calendar(example_plugin)

    with create_session() as session:
        on_call_events = list(session.scalars(select(OnCallEvent).order_by(OnCallEvent.start_event_utc)).all())
        assert len(on_call_events) == 3
        for on_call_event in on_call_events:
            assert on_call_event.calendar_uid == "data_platform_duty"
        assert on_call_events[0].person.username == "jan"
        assert on_call_events[0].person.email is None

        assert on_call_events[1].person.username is None
        assert on_call_events[1].person.email == "jan@schoenmaker.nl"

        assert on_call_events[2].person.username is None
        assert on_call_events[2].person.email == "henk@tank.nl"
