from datetime import timedelta
from typing import List, Optional, Tuple

import requests_mock
from pendulum.datetime import DateTime

from duty_board.alchemy import settings
from duty_board.models.calendar import Calendar
from duty_board.models.person import Person
from duty_board.plugin.example.example_plugin import ExamplePlugin
from tests import ical_helper
from tests.conftest import get_loaded_ldap_plugin


def test_sync_calendar(set_up_persons: Person) -> None:
    calendar = Calendar(
        uid="duty-board-test-calendar",
        name="DutyBoard Test calendar",
        description="We will mock this request anyway",
        category="Big Data",
        order=1,
        icalendar_url="https://non-existing-url.com/icalendar.ics",
    )
    plugin: ExamplePlugin
    with get_loaded_ldap_plugin() as plugin, requests_mock.Mocker() as m:
        events: List[Tuple[Optional[str], Optional[str], timedelta, timedelta]] = [
            ("piet", None, timedelta(days=-2), timedelta(days=1)),
            ("jan", None, timedelta(days=0), timedelta(days=1)),
            ("jan", "mailto:jan@schoenmaker.nl", timedelta(days=1), timedelta(days=1)),
            ("someone", None, timedelta(days=22), timedelta(days=20)),
            ("henkietankie", "henk@tank.nl", timedelta(days=2), timedelta(days=20)),
            ("non-existing", None, timedelta(days=42), timedelta(days=20)),
        ]
        ical_response = ical_helper.get_icalendar_response(events=events)
        m.get("https://non-existing-url.com/icalendar.ics", text=ical_response)
        calendar = plugin.sync_calendar(calendar=calendar, session=settings.Session())

        def get_timestamp(delta: timedelta) -> str:
            return f"{(DateTime.utcnow() + delta).strftime('%Y-%m-%d')}T02:00:00+00:00"

        assert len(calendar.events) == 4
        assert calendar.events[0].person.username == "jan"
        assert calendar.events[0].person.email == "jan@schoenmaker.nl"
        assert str(calendar.events[0].start_event_utc) == get_timestamp(timedelta(days=0))
        assert str(calendar.events[0].end_event_utc) == get_timestamp(timedelta(days=1))
        assert calendar.events[1].person.username == "jan"
        assert calendar.events[1].person.email == "jan@schoenmaker.nl"
        assert calendar.events[0].person.uid == calendar.events[1].person.uid
        assert str(calendar.events[1].start_event_utc) == get_timestamp(timedelta(days=1))
        assert str(calendar.events[1].end_event_utc) == get_timestamp(timedelta(days=2))
        assert calendar.events[2].person.username == "henk"
        assert calendar.events[2].person.email == "henk@tank.nl"
        assert str(calendar.events[2].start_event_utc) == get_timestamp(timedelta(days=2))
        assert str(calendar.events[2].end_event_utc) == get_timestamp(timedelta(days=22))
        assert calendar.events[3].person.username == "someone"
        assert calendar.events[3].person.email is None
        assert str(calendar.events[3].start_event_utc) == get_timestamp(timedelta(days=22))
        assert str(calendar.events[3].end_event_utc) == get_timestamp(timedelta(days=42))
