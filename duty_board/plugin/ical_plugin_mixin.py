from __future__ import annotations

import logging
from typing import List, Optional

import pytz
import requests  # type: ignore
from ical_library import client
from ical_library.ical_components import VCalendar, VEvent
from ical_library.timeline import Timeline
from pendulum import DateTime, Duration
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person

logger = logging.getLogger(__name__)


class ICalPluginMixin:
    @staticmethod
    def _get_icalendar(icalendar_url: str) -> str:
        response = requests.get(icalendar_url, timeout=5.0)
        response.raise_for_status()
        return response.text

    def _get_events_for_upcoming_month(self, icalendar_url: str, event_prefix: str, limit: int = 10) -> List[VEvent]:
        """Gets the calendar events for the upcoming 4 weeks."""
        logger.info(f"Loading {icalendar_url}, this might take some time.")
        now = DateTime.now()
        month_from_now = now + Duration(days=7 * 4)
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

    def _get_or_create_person(self, value: str) -> int:
        """Returns a Person object if the person is not already in the database."""
        session: SASession
        with create_session() as session:
            if "@" in value:
                result = session.query(Person).filter(Person.email == value).first()
            else:
                result = session.query(Person).filter(Person.username == value).first()
            if result:
                return result.uid
            username = None if "@" in value else value
            email = value if "@" in value else None
            person = Person(
                username=username,
                email=email,
                img_filename=None,
                extra_attributes_json=None,
                last_update_utc=DateTime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
                sync=True,
            )
            session.add(person)
        # This extra call is needed to fetch the UID that is automatically created for the Person.
        with create_session() as session:
            result = session.query(Person).filter(Person.username == username).filter(Person.email == email).first()
            if result is None:
                raise ValueError(f"We just added Person {username=} {email=} and we already can't find him anymore..")
            return result.uid

    def _create_on_call_event(self, calendar: Calendar, v_event: VEvent, person_uid: int) -> OnCallEvent:
        return OnCallEvent(
            calendar_uid=calendar.uid,
            start_event_utc=v_event.start,
            end_event_utc=v_event.end,
            person_uid=person_uid,
        )

    def sync_calendar(self, calendar: Calendar, event_prefix: str | None, session: SASession) -> Calendar:
        items_to_insert: List[OnCallEvent] = []
        session.query(OnCallEvent).filter(OnCallEvent.calendar_uid == calendar.uid).delete()
        event: VEvent
        for event in self._get_events_for_upcoming_month(calendar.icalendar_url, event_prefix or ""):
            # First attempt attendee. If that is not set, we look at the title/summary of the event.
            person_unique_identifier: Optional[str] = None
            if event.attendee is not None and any(event.attendee):
                person_unique_identifier = event.attendee[0].value
            if person_unique_identifier is None:
                assert event.summary is not None and event.summary.value is not None  # for Mypy :)
                person_unique_identifier = event.summary.value
                if not person_unique_identifier:
                    raise ValueError(f"{event.summary.value=} should not be None.")
            person_information_str = person_unique_identifier[len(event_prefix or "") :]
            person_uid: int = self._get_or_create_person(person_information_str)
            on_call_event: OnCallEvent = self._create_on_call_event(calendar, event, person_uid=person_uid)
            items_to_insert.append(on_call_event)
        session.bulk_save_objects(items_to_insert)
        return calendar
