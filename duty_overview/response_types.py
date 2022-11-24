import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class _Person(BaseModel):
    ldap: str
    email: str
    extra_attributes: Dict[str, Any]
    last_update_utc: datetime.datetime
    error_msg: str
    sync: bool


class _Events(BaseModel):
    start_event_utc: datetime.datetime
    end_event_utc: datetime.datetime
    person_uid: int


class _Calendar(BaseModel):
    uid: str
    name: str
    description: str
    category: str
    order: int
    last_update_utc: datetime.datetime
    error_msg: str
    sync: bool
    events: List[_Events]


class CurrentSchedule(BaseModel):
    calendars: List[_Calendar]
    persons: Dict[int, _Person]
