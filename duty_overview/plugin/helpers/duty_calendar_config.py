from __future__ import annotations

from attrs import define, field, validators


@define
class DutyCalendarConfig:
    # A unique identifier that stays the same. When renaming the name object and keeping the same uid, it won't remove
    # all your events & persons in the meantime.
    uid: str = field(validator=[validators.instance_of(str), validators.max_len(50)])
    # The name shown on the UI.
    name: str = field(validator=[validators.instance_of(str), validators.max_len(200)])
    # A description about who owns what.
    description: str | None = field(
        validator=validators.optional([validators.instance_of(str), validators.max_len(5000)])
    )
    # iCalendar URL. This has to be something our request library can fetch.
    icalendar_url: str = field(validator=[validators.instance_of(str), validators.max_len(500)])
    # The category this duty belongs in (this is what menu item it is shown for)
    category: str | None = field(default="default", validator=[validators.instance_of(str), validators.max_len(50)])
    # Priority of order. The higher the number, the earlier this calendar shows up.
    order: int = field(default=999, validator=[validators.instance_of(int), validators.ge(0), validators.le(9999999)])
    # Prefix before user LDAP or user email is mentioned. Example prefix; 'duty:' when calendar event; 'duty: thomas'
    event_prefix: str | None = field(
        default=None, validator=validators.optional([validators.instance_of(str), validators.max_len(50)])
    )
