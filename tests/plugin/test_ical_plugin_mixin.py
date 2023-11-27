import random
import string
from datetime import timedelta
from typing import Iterable, List, Optional, Tuple

import pytest
import requests_mock
from pendulum.datetime import DateTime

from duty_board.alchemy import settings
from duty_board.models.calendar import Calendar
from duty_board.plugin.example.example_plugin import ExamplePlugin
from tests.conftest import get_loaded_ldap_plugin


def _get_icalender_event(
    username: Optional[str], email: Optional[str], delta_start: timedelta, delta_end: timedelta
) -> str:
    start = DateTime.now() + delta_start
    end = start + delta_end
    attendee = f"ATTENDEE:{email}\n" if email else ""
    return f"""BEGIN:VEVENT
DTSTART;VALUE=DATE-TIME:{start.strftime("%Y%m%d")}T020000Z
DTEND;VALUE=DATE-TIME:{end.strftime("%Y%m%d")}T020000Z
{attendee}UID:{''.join(random.sample(string.ascii_lowercase, 14))}
URL:https://adyen.pagerduty.com/schedules#P5IHOP7
SUMMARY:{username}
END:VEVENT"""


def get_icalendar_response(events: Iterable[Tuple[Optional[str], Optional[str], timedelta, timedelta]]) -> str:
    start_text = """BEGIN:VCALENDAR
PRODID;X-RICAL-TZSOURCE=TZINFO:-//com.denhaven2/NONSGML ri_cal gem//EN
CALSCALE:GREGORIAN
VERSION:2.0
X-WR-CALNAME:On Call Schedule for Data-duty"""
    end_text = "END:VCALENDAR"
    events_str = [
        _get_icalender_event(username=username, email=email, delta_start=delta_start, delta_end=delta_end)
        for username, email, delta_start, delta_end in events
    ]
    event_text = "\n".join(events_str)
    return f"{start_text}\n{event_text}\n{end_text}"


@pytest.mark.usefixtures("_set_up_persons")
def test_sync_calendar() -> None:
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
        ical_response = get_icalendar_response(events=events)
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
