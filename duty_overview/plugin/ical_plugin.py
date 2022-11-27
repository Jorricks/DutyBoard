from __future__ import annotations

import json
import logging
from typing import List, Optional

from ical_library import client
from ical_library.ical_components import VEvent, VCalendar
from ical_library.timeline import Timeline
from pendulum import DateTime, Duration
import pytz
from sqlalchemy.orm import Session as SASession

from duty_overview.alchemy.session import create_session
from duty_overview.models.calendar import Calendar
from duty_overview.models.on_call_event import OnCallEvent
from duty_overview.models.person import Person
from duty_overview.plugin.standard_plugin import StandardPlugin

logger = logging.getLogger(__name__)


class ICalPlugin(StandardPlugin):
    @staticmethod
    def _get_events_for_upcoming_month(icalendar_url: str, prefix: str, limit: int = 10) -> List[VEvent]:
        """Gets the calendar events for the upcoming 4 weeks."""
        logger.info(f"Loading {icalendar_url}, this might take some time.")
        now = DateTime.now()
        month_from_now = now + Duration(days=7*4)
        calendar: VCalendar = client.parse_icalendar_url(icalendar_url)
        # timeline is ordered by start date.
        timeline: Timeline = calendar.get_limited_timeline(now, month_from_now)
        return [
            event
            for event in timeline.overlapping(now, month_from_now)
            if isinstance(event, VEvent) and event.summary.value and event.summary.value.startswith(prefix)
        ][:limit]

    def _get_or_create_person(self, value: str) -> int:
        """Returns a Person object if the person is not already in the database."""
        session: SASession
        with create_session() as session:
            if "@" in value:
                result = session.query(Person).filter(Person.ldap == value).first()
            else:
                result = session.query(Person).filter(Person.email == value).first()
            if result:
                return result.uid
            ldap = None if "@" in value else value
            email = value if "@" in value else None
            person = Person(
                ldap=ldap,
                email=email,
                extra_attributes_json=json.dumps({}),
                last_update_utc=DateTime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
                sync=True
            )
            session.add(person)
        with create_session() as session:
            result = session.query(Person).filter(Person.ldap == ldap).filter(Person.email == email).first()
            if result is None:
                raise ValueError(f"We just added Person {ldap=} {email=} and we already can't find him anymore..")
            return result.uid

    def _create_on_call_event(self, calendar: Calendar, v_event: VEvent, person_uid: int) -> OnCallEvent:
        return OnCallEvent(
            calendar_uid=calendar,
            start_event_utc=v_event.start,
            end_event_utc=v_event.end,
            person_uid=person_uid,
        )

    def sync_calendar(self, calendar: Calendar, prefix: str | None, session: SASession) -> None:
        items_to_insert: List[OnCallEvent] = []
        session.query(OnCallEvent).filter(OnCallEvent.calendar_uid == calendar.uid).delete()
        event: VEvent
        for event in self._get_events_for_upcoming_month(calendar.icalendar_url, prefix or ""):
            person_information_str: Optional[str] = event.summary.value
            if not person_information_str:
                raise ValueError(f"{event.summary.value=} should not be None.")
            person_information_str = person_information_str[len(prefix or ""):]
            person_uid: int = self._get_or_create_person(person_information_str)
            on_call_event: OnCallEvent = self._create_on_call_event(calendar, event, person_uid=person_uid)
            items_to_insert.append(on_call_event)
        session.bulk_save_objects(items_to_insert)
