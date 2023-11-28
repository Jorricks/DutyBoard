import datetime
from typing import List

from pendulum.tz.timezone import UTC
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.plugin.helpers.duty_calendar_config import DutyCalendarConfig


def _create_or_update_calendar(session: SASession, calendar: DutyCalendarConfig) -> None:
    calendar_db_instance = session.scalars(select(Calendar).where(Calendar.uid == calendar.uid)).one_or_none()
    if calendar_db_instance is not None:
        calendar_db_instance.name = calendar.name
        calendar_db_instance.description = calendar.description
        calendar_db_instance.category = calendar.category  # type: ignore[assignment]
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
            last_update_utc=datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
            sync=True,
        )
        session.add(calendar_db_instance)


def sync_duty_calendar_configurations_to_postgres(
    session: SASession,
    duty_calendar_configurations: List[DutyCalendarConfig],
) -> None:
    for duty_calendar_config in duty_calendar_configurations:
        _create_or_update_calendar(session, duty_calendar_config)
    all_described_calendar_uids: List[str] = [dcc.uid for dcc in duty_calendar_configurations]
    session.execute(delete(Calendar).where(Calendar.uid.not_in(all_described_calendar_uids)))
