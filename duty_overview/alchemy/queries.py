import datetime
import json
from collections import defaultdict
from typing import Dict, List, Optional, Set

from pendulum import DateTime
from pytz.tzinfo import BaseTzInfo
from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.on_call_event import OnCallEvent
from duty_overview.models.person import Person
from duty_overview.response_types import _Calendar, _Events, _Person


def format_datetime_for_timezone(dt: datetime.datetime, timezone: Optional[BaseTzInfo]) -> str:
    dt_tz_aware = dt.astimezone(timezone) if timezone else dt.astimezone()
    return dt_tz_aware.strftime("%Y-%m-%d %H:%M:%S")


def _get_events_ending_from_now_onwards(
    session: SASession, all_encountered_person_uids: Set[int], timezone: Optional[BaseTzInfo]
) -> Dict[str, List[_Events]]:
    result: List[OnCallEvent] = session.query(OnCallEvent).filter(OnCallEvent.end_event_utc >= DateTime.utcnow()).all()
    mapped: Dict[str, List[_Events]] = defaultdict(list)
    for calendar_event in result:
        mapped[calendar_event.calendar_uid].append(
            _Events(
                start_event=format_datetime_for_timezone(calendar_event.start_event_utc, timezone),
                end_event=format_datetime_for_timezone(calendar_event.end_event_utc, timezone),
                person_uid=calendar_event.person_uid,
            )
        )
        all_encountered_person_uids.add(calendar_event.person_uid)
    return mapped


def get_calendars(
    session: SASession, all_encountered_person_uids: Set[int], timezone: Optional[BaseTzInfo]
) -> List[_Calendar]:
    events: Dict[str, List[_Events]] = _get_events_ending_from_now_onwards(
        session=session, all_encountered_person_uids=all_encountered_person_uids, timezone=timezone
    )
    result: List[Calendar] = session.query(Calendar).all()
    return [
        _Calendar(
            uid=single_calendar.uid,
            name=single_calendar.name,
            description=single_calendar.description,
            category=single_calendar.category,
            order=single_calendar.order,
            last_update=format_datetime_for_timezone(single_calendar.last_update_utc, timezone),
            error_msg=single_calendar.error_msg or "",
            sync=single_calendar.sync,
            events=events.get(single_calendar.uid),
        )
        for single_calendar in result
    ]


def get_persons(session: SASession, all_person_uids: Set[int], timezone: Optional[BaseTzInfo]) -> Dict[int, _Person]:
    result: List[Person] = session.query(Person).where(Person.uid.in_(all_person_uids))
    return {
        a_person.uid: _Person(
            ldap=a_person.ldap,
            email=a_person.email,
            extra_attributes=(json.loads(a_person.extra_attributes_json) if a_person.extra_attributes_json else {}),
            last_update=format_datetime_for_timezone(a_person.last_update_utc, timezone),
            error_msg=a_person.error_msg or "",
            sync=a_person.sync,
        )
        for a_person in result
    }
