import logging
from typing import List, Optional, Tuple

import pytz
import requests
from ical_library import client
from ical_library.help_modules import dt_utils
from ical_library.ical_components.v_calendar import VCalendar
from ical_library.ical_components.v_event import VEvent
from ical_library.timeline import Timeline
from pendulum.datetime import DateTime
from pendulum.duration import Duration
from sqlalchemy import Select, select
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person

logger = logging.getLogger(__name__)


class ICalPluginMixin:
    @staticmethod
    def _get_icalendar(icalendar_url: str) -> str:
        response = requests.get(icalendar_url, timeout=30.0)  # For larger calendars, it might take quite some time.
        response.raise_for_status()
        return response.text

    def _get_events_for_upcoming_month(self, icalendar_url: str, event_prefix: str, limit: int = 10) -> List[VEvent]:
        """Gets the calendar events for the upcoming 4 weeks."""
        logger.info(f"Loading {icalendar_url}, this might take some time.")
        now = DateTime.now()
        month_from_now = now + Duration(days=7 * 4)  # type: ignore[no-untyped-call]
        calendar_txt: str = self._get_icalendar(icalendar_url=icalendar_url)
        calendar: VCalendar = client.parse_lines_into_calendar(calendar_txt)
        # timeline is ordered by start date.
        timeline: Timeline = calendar.get_limited_timeline(now, month_from_now)
        return [
            event
            for event in timeline.overlapping(now, month_from_now)
            if isinstance(event, VEvent)
            and event.summary is not None
            and event.summary.value is not None
            and event.summary.value.startswith(event_prefix)
        ][:limit]

    def _get_or_create_person(self, value: str) -> Person:
        """Returns a Person object if the person is not already in the database."""
        session: SASession
        with create_session() as session:
            if "@" in value:
                stmt: Select[Tuple[Person]] = select(Person).where(Person.email == value)
            else:
                stmt = select(Person).where(Person.username == value)
            result: Optional[Person] = session.scalar(stmt)
            if result:
                return result
            username = None if "@" in value else value
            email = value if "@" in value else None
            return Person(
                username=username,
                email=email,
                image=None,
                img_width=None,
                img_height=None,
                extra_attributes_json=None,
                last_update_utc=DateTime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),  # type: ignore[no-untyped-call]
                sync=True,
            )

    def _create_on_call_event(self, calendar: Calendar, v_event: VEvent, person: Person) -> OnCallEvent:
        return OnCallEvent(
            calendar_uid=calendar.uid,
            start_event_utc=dt_utils.convert_time_object_to_aware_datetime(v_event.start),
            end_event_utc=dt_utils.convert_time_object_to_aware_datetime(v_event.end),
            person=person,
        )

    def sync_calendar(self, calendar: Calendar, session: SASession) -> Calendar:  # noqa: ARG002
        calendar.events = []
        event: VEvent
        for event in self._get_events_for_upcoming_month(calendar.icalendar_url, calendar.event_prefix or ""):
            # First attempt attendee. If that is not set, we look at the title/summary of the event.
            person_unique_identifier: Optional[str] = None
            if event.attendee is not None and any(event.attendee):
                person_unique_identifier = (event.attendee[0].value or "").replace("mailto:", "") or None
            if person_unique_identifier is None:
                if event.summary is None or event.summary.value is None:
                    raise TypeError(f"Unexpected value for {event.summary=}.")  # Make Mypy happy :)
                person_unique_identifier = event.summary.value
                if not person_unique_identifier:
                    raise ValueError(f"{event.summary.value=} should not be None.")
                person_information_str: str = person_unique_identifier[len(calendar.event_prefix or "") :]
            else:
                person_information_str = person_unique_identifier
            person: Person = self._get_or_create_person(person_information_str)
            on_call_event: OnCallEvent = self._create_on_call_event(calendar, event, person)
            calendar.events.append(on_call_event)
        return calendar
