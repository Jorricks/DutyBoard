from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class DutyCalendarConfig(BaseModel):
    # A unique identifier that stays the same. When renaming the name object and keeping the same uid, it won't remove
    # all your events & persons in the meantime.
    uid: Annotated[str, Field(max_length=50)]
    # The name shown on the UI.
    name: Annotated[str, Field(max_length=200)]
    # A description about who owns what.
    description: Annotated[Optional[str], Field(max_length=5000)]
    # iCalendar URL. This has to be something our request library can fetch.
    icalendar_url: Annotated[str, Field(max_length=500)]
    # The category this duty belongs in (this is what menu item it is shown for)
    category: Annotated[Optional[str], Field(max_length=50)]
    # Priority of order. The lower the number, the earlier this calendar shows up.
    order: Annotated[int, Field(default=99999, ge=0, le=9999999)]
    # Prefix before user LDAP or user email is mentioned. Example prefix; 'duty:' when calendar event; 'duty: thomas'
    event_prefix: Annotated[Optional[str], Field(max_length=50, default=None)]
