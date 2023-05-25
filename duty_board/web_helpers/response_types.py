from typing import Dict, List, Optional

from pydantic import BaseModel


class _PersonEssentials(BaseModel):
    uid: int
    username: Optional[str]
    email: Optional[str]


class _Events(BaseModel):
    start_event: str
    end_event: str
    person_uid: int


class _Calendar(BaseModel):
    uid: str
    name: str
    description: str
    category: str
    order: int
    last_update: str
    error_msg: str
    sync: bool
    events: List[_Events]


class _Config(BaseModel):
    timezone: str
    text_color: str
    background_color: str
    categories: List[str]
    git_repository_url: Optional[str]
    enable_admin_button: bool
    announcement_text_color: str
    announcement_background_color: str
    announcements: List[str]
    footer_html: Optional[str]


class CurrentSchedule(BaseModel):
    config: _Config
    calendars: List[_Calendar]
    persons: Dict[int, _PersonEssentials]


class _ExtraInfoOnPerson(BaseModel):
    information: str
    icon: str
    icon_color: str
    url: Optional[str]


class PersonResponse(BaseModel):
    uid: str
    username: Optional[str]
    email: Optional[str]
    img_filename: Optional[str]
    img_width: Optional[int]
    img_height: Optional[int]
    extra_attributes: List[_ExtraInfoOnPerson]
    last_update: str
    error_msg: str
    sync: bool
