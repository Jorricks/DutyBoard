import datetime
from collections import defaultdict
from typing import List, Dict, Any, Set

import pendulum
from fastapi import FastAPI
from pendulum import DateTime
from pydantic import BaseModel
from sqlalchemy.orm import Session as SASession

from models.calendar import Calendar
from models.on_call_event import OnCallEvent
from session import provide_session


class _Person(BaseModel):
    uid: int
    ldap: str
    email: str
    attributes: Dict[str, Any]
    last_update_utc: datetime.datetime
    sync: bool


class _Events(BaseModel):
    start_event_utc: datetime.datetime
    end_event_utc: datetime.datetime
    person_uid: int


class _Calendar(BaseModel):
    uid: str
    name: str
    description: str
    last_update_utc: datetime.datetime
    sync: bool
    events: List[_Events]


class CurrentSchedule(BaseModel):
    calendars: List[_Calendar]
    persons: List[_Person]


app = FastAPI()


def get_events_ending_from_now_onwards(
    session: SASession, all_encountered_person_uids: Set[int]
) -> Dict[str, List[_Events]]:
    result: List[OnCallEvent] = (
        session.query(OnCallEvent).filter(OnCallEvent.end_event >= DateTime.utcnow()).all()
    )
    mapped: Dict[str, List[_Events]] = defaultdict(list)
    for calendar_event in result:
        mapped[calendar_event.calendar_uid].append(_Events(
            start_event_utc=calendar_event.start_event,
            end_event_utc=calendar_event.end_event,
            person_uid=calendar_event.person_uid,
        ))
        all_encountered_person_uids.add(calendar_event.person_uid)
    return mapped


def get_calendars(session: SASession, all_encountered_person_uids: Set[int]) -> List[_Calendar]:
    events: Dict[str, List[_Events]] = get_events_ending_from_now_onwards(session, all_encountered_person_uids)
    result: List[Calendar] = session.query(Calendar).all()
    return [
        Calendar(
            uid=single_calendar.uid,
            name=single_calendar.name,
            description=single_calendar.description,
            last_update_utc=single_calendar.last_update,
            sync=single_calendar.sync,
            events=events.get(single_calendar.uid),
        )
        for single_calendar in result
    ]


def get_persons(session: SASession, all_person_uids: Set[int]) -> List[_Person]:
    raise NotImplementedError()


@app.get("/get_schedule/", response_model=CurrentSchedule)
@provide_session
async def get_schedule(session: SASession):
    all_encountered_person_uids: Set[int] = set()
    calendars: List[_Calendar] = get_calendars(session, all_encountered_person_uids)
    persons: List[_Person] = get_persons(session, all_encountered_person_uids)
    return CurrentSchedule(
        calendars=calendars,
        persons=persons
    )
