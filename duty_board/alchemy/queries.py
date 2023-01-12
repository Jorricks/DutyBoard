import datetime
import json
from collections import defaultdict
from typing import Dict, List, Optional, Set

from pendulum import DateTime, UTC
from pytz.tzinfo import BaseTzInfo
from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.plugin.helpers.duty_calendar_config import DutyCalendarConfig
from duty_board.web_helpers.response_types import _Calendar, _Events, _ExtraInfoOnPerson, _Person, PersonResponse


def format_datetime_for_timezone(dt: datetime.datetime, timezone: BaseTzInfo) -> str:
    dt_tz_aware = dt.astimezone(timezone)
    return dt_tz_aware.strftime("%Y-%m-%d %H:%M:%S")


def _get_events_ending_from_now_onwards(
    session: SASession, all_encountered_person_uids: Set[int], timezone: BaseTzInfo
) -> Dict[str, List[_Events]]:
    result = session.query(OnCallEvent).filter(OnCallEvent.end_event_utc >= DateTime.utcnow()).all()
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


def get_calendars(session: SASession, all_encountered_person_uids: Set[int], timezone: BaseTzInfo) -> List[_Calendar]:
    events: Dict[str, List[_Events]] = _get_events_ending_from_now_onwards(
        session=session, all_encountered_person_uids=all_encountered_person_uids, timezone=timezone
    )
    result = session.query(Calendar).order_by(Calendar.order).all()
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
            events=events.get(single_calendar.uid) or [],
        )
        for single_calendar in result
    ]


def get_persons(session: SASession, all_person_uids: Set[int], timezone: BaseTzInfo) -> Dict[int, _Person]:
    result = session.query(Person).where(Person.uid.in_(all_person_uids))
    return {
        a_person.uid: _Person(
            uid=a_person.uid,
            username=a_person.username,
            email=a_person.email,
            img_filename=a_person.img_filename,
            extra_attributes={},
            last_update=format_datetime_for_timezone(a_person.last_update_utc, timezone),
            error_msg=a_person.error_msg or "",
            sync=a_person.sync,
        )
        for a_person in result
    }


def parse_extra_attributes(person_uid: int, extra_attributes_str: Optional[str]) -> List[_ExtraInfoOnPerson]:
    if extra_attributes_str is None or len(extra_attributes_str) == 0:
        return []

    extra_attributes_list = json.loads(extra_attributes_str)
    if not isinstance(extra_attributes_list, dict):
        raise ValueError(f"Expected extra_attributes field to be a dict for {person_uid=}.")

    result_list: List[_ExtraInfoOnPerson] = []
    value: Dict[str, str]
    for key, value in extra_attributes_list.items():
        if not isinstance(value, dict):
            raise ValueError(f"Expected extra_attributes[{key}] field to be a dict for {person_uid=}.")
        if "information" not in value.keys():
            raise ValueError(f"Missing required extra_attributes[{key}][information] for {person_uid=}.")
        result_list.append(
            _ExtraInfoOnPerson(
                information=value.get("information"),
                icon=value.get("icon", "FaMinus"),
                icon_color=value.get("icon_color", "black"),
                url=value.get("url", None),
            )
        )
    return result_list


def get_person(session: SASession, person_uid: int, timezone: BaseTzInfo) -> PersonResponse:
    person = session.query(Person).where(Person.uid == person_uid).first()
    if person is None:
        raise ValueError(f"Invalid {person_uid=} passed.")

    return PersonResponse(
        uid=person.uid,
        username=person.username,
        email=person.email,
        img_filename=person.img_filename,
        extra_attributes=parse_extra_attributes(person_uid, extra_attributes_str=person.extra_attributes_json),
        last_update=format_datetime_for_timezone(person.last_update_utc, timezone),
        error_msg=person.error_msg or "",
        sync=person.sync,
    )


def _create_or_update_calendar(session: SASession, calendar: DutyCalendarConfig) -> None:
    calendar_db_instance = session.query(Calendar).where(Calendar.uid == calendar.uid).first()
    if calendar_db_instance is not None:
        calendar_db_instance.name = calendar.name
        calendar_db_instance.description = calendar.description
        calendar_db_instance.category = calendar.category
        calendar_db_instance.order = calendar.order
        calendar_db_instance.icalendar_url = calendar.icalendar_url
        calendar_db_instance.event_prefix = calendar.event_prefix
        session.merge(calendar_db_instance)
    else:
        calendar_db_instance = Calendar(
            uid=calendar.uid,
            name=calendar.name,
            description=calendar.description,
            category=calendar.category,
            order=calendar.order,
            icalendar_url=calendar.icalendar_url,
            event_prefix=calendar.event_prefix,
            error_msg=None,
            last_update_utc=DateTime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
            sync=True,
        )
        session.add(calendar_db_instance)


def sync_duty_calendar_configurations_to_postgres(
    session: SASession, duty_calendar_configurations: List[DutyCalendarConfig]
) -> None:
    for duty_calendar_config in duty_calendar_configurations:
        _create_or_update_calendar(session, duty_calendar_config)
    all_described_calendar_uids: List[str] = [dcc.uid for dcc in duty_calendar_configurations]
    session.query(Calendar).where(Calendar.uid.not_in(all_described_calendar_uids)).delete()
