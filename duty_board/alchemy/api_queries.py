import datetime
import json
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set

from pendulum.datetime import DateTime
from pytz.tzinfo import BaseTzInfo
from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.web_helpers.response_types import (
    PersonResponse,
    _Calendar,
    _Events,
    _ExtraInfoOnPerson,
    _PersonEssentials,
)


def format_datetime_for_timezone(dt: datetime.datetime, timezone: BaseTzInfo) -> str:
    dt_tz_aware = dt.astimezone(timezone)
    return dt_tz_aware.strftime("%Y-%m-%d %H:%M:%S %Z")


def _get_events_ending_from_now_onwards(
    session: SASession,
    all_encountered_person_uids: Set[int],
    timezone: BaseTzInfo,
) -> Dict[str, List[_Events]]:
    stmt = select(OnCallEvent).where(OnCallEvent.end_event_utc >= DateTime.utcnow())
    result: Iterable[OnCallEvent] = session.scalars(stmt).all()
    mapped: Dict[str, List[_Events]] = defaultdict(list)
    for calendar_event in result:
        mapped[calendar_event.calendar_uid].append(
            _Events(
                start_event=format_datetime_for_timezone(calendar_event.start_event_utc, timezone),
                end_event=format_datetime_for_timezone(calendar_event.end_event_utc, timezone),
                person_uid=calendar_event.person_uid,
            ),
        )
        all_encountered_person_uids.add(calendar_event.person_uid)
    return mapped


def get_calendars(session: SASession, all_encountered_person_uids: Set[int], timezone: BaseTzInfo) -> List[_Calendar]:
    events: Dict[str, List[_Events]] = _get_events_ending_from_now_onwards(
        session=session,
        all_encountered_person_uids=all_encountered_person_uids,
        timezone=timezone,
    )
    result: Iterable[Calendar] = session.scalars(select(Calendar).order_by(Calendar.order)).all()
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


def get_peoples_essentials(session: SASession, all_person_uids: Set[int]) -> Dict[int, _PersonEssentials]:
    result: Iterable[Person] = session.scalars(select(Person).where(Person.uid.in_(all_person_uids))).all()
    return {
        a_person.uid: _PersonEssentials(
            uid=a_person.uid,
            username=a_person.username,
            email=a_person.email,
        )
        for a_person in result
    }


def parse_extra_attributes(person_uid: int, extra_attributes_str: Optional[str]) -> List[_ExtraInfoOnPerson]:
    if extra_attributes_str is None or len(extra_attributes_str) == 0:
        return []

    extra_attributes_list = json.loads(extra_attributes_str)
    if not isinstance(extra_attributes_list, dict):
        raise TypeError(f"Expected extra_attributes field to be a dict for {person_uid=}.")

    result_list: List[_ExtraInfoOnPerson] = []
    value: Dict[str, str]
    for key, value in extra_attributes_list.items():
        if not isinstance(value, dict):
            raise TypeError(f"Expected extra_attributes[{key}] field to be a dict for {person_uid=}.")
        if "information" not in value:
            raise ValueError(f"Missing required extra_attributes[{key}][information] for {person_uid=}.")
        result_list.append(
            _ExtraInfoOnPerson(
                information=value["information"],
                icon=value.get("icon", "FaMinus"),
                icon_color=value.get("icon_color", "black"),
                url=value.get("url", None),
            ),
        )
    return result_list


def get_person(session: SASession, person_uid: int, timezone: BaseTzInfo) -> PersonResponse:
    person = session.scalars(select(Person).where(Person.uid == person_uid)).one_or_none()
    if person is None:
        raise ValueError(f"Invalid {person_uid=} passed.")

    return PersonResponse(
        uid=person.uid,
        username=person.username,
        email=person.email,
        img_filename=str(person.image_uid) if person.image_uid is not None else None,
        img_width=person.img_width,
        img_height=person.img_height,
        extra_attributes=parse_extra_attributes(person_uid, extra_attributes_str=person.extra_attributes_json),
        last_update=format_datetime_for_timezone(person.last_update_utc, timezone),
        error_msg=person.error_msg or "",
        sync=person.sync,
    )
