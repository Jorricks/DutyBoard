import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Set, Union

from pendulum.datetime import DateTime
from prometheus_client import Counter, Gauge
from sqlalchemy import select
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.plugin.abstract_plugin import AbstractPlugin

logger = logging.getLogger(__name__)

update_event_checker_run_counter = Counter(
    "duty_calendars_refresh_counter", "Count the number of update event check runs."
)
update_event_callback_counter = Counter(
    "update_event_callback_counter", "Count the number of callbacks executed for update events."
)
update_event_callback_success_counter = Counter(
    "duty_calendars_refresh_success_counter", "Count the number of callbacks for update events that succeed."
)
update_event_callback_failed_counter = Counter(
    "duty_calendars_refresh_failed_counter", "Count the number of callbacks for update events that fail."
)
updated_event_callback_failed = Gauge(
    "duty_calendars_last_refresh_failed", "Indicate whether the last callback failed", ["calendar_name"]
)


def run_callback_for_calendar_with_new_duty(plugin: AbstractPlugin, calendar: Calendar, persons: Set[Person]) -> None:
    update_event_checker_run_counter.inc()
    failed: bool = False
    try:
        logger.info(f"Running callback 'handle_new_person_on_duty_event' for {calendar=}, {persons=}.")
        plugin.handle_new_person_on_duty_event(calendar=calendar, persons=persons)
        logger.info(f"Callback succeeded 'handle_new_person_on_duty_event' for {calendar=}, {persons=}.")
    except Exception:
        failed = True
        logger.exception("Failed to update some calendar in the database. There is probably some database error.")

    if calendar is not None:
        updated_event_callback_failed.labels(calendar.name).set(int(failed))
    if failed:
        update_event_callback_failed_counter.inc()
    else:
        update_event_callback_success_counter.inc()


def get_all_person_uids_on_duty_per_calendar(session: SASession) -> Dict[str, Set[int]]:
    stmt = (
        select(OnCallEvent)
        .where(OnCallEvent.start_event_utc <= DateTime.utcnow())
        .where(OnCallEvent.end_event_utc > DateTime.utcnow())
    )
    result: Iterable[OnCallEvent] = session.scalars(stmt).all()
    mapped: Dict[str, Set[int]] = defaultdict(set)
    for calendar_event in result:
        mapped[calendar_event.calendar_uid].add(calendar_event.person_uid)
    return mapped


def get_calendars_with_new_duty(
    session: SASession, last_calendar_uid_to_person_id: Dict[str, Union[Set[int], None]]
) -> Dict[str, Set[int]]:
    updated_calendars: Dict[str, Set[int]] = {}
    person_uids_on_duty_per_calendar: Dict[str, Set[int]] = get_all_person_uids_on_duty_per_calendar(session=session)

    all_calendars: Iterable[Calendar] = session.scalars(select(Calendar).order_by(Calendar.order)).all()
    for calendar in all_calendars:
        person_uids_on_duty = person_uids_on_duty_per_calendar[calendar.uid]
        if person_uids_on_duty == last_calendar_uid_to_person_id[calendar.uid]:
            logger.debug(f"{calendar=} had no update in terms of Duty.")
        else:
            last_calendar_uid_to_person_id[calendar.uid] = person_uids_on_duty
            updated_calendars[calendar.uid] = person_uids_on_duty
            logger.info(f"Found new people on Duty for {calendar=}, {person_uids_on_duty=}.")
    return updated_calendars


def run_update_event_loop(
    session: SASession,
    plugin: AbstractPlugin,
    calendars_with_new_on_call: Dict[str, Set[int]],
) -> None:
    for calendar_uid_with_new_duty, new_duty_uids in calendars_with_new_on_call.items():
        calendar_stmt = select(Calendar).where(Calendar.uid == calendar_uid_with_new_duty)
        result: List[Calendar] = list(session.scalars(calendar_stmt).all())
        logger.debug(f"Fetching {calendar_uid_with_new_duty=} gave {result=}.")
        calendar: Calendar = result[0]

        person_stmt = select(Person).where(Person.uid.in_(new_duty_uids))
        persons: Set[Person] = set(session.scalars(person_stmt).all())
        logger.debug(f"Fetching {new_duty_uids=} gave {persons=}.")

        run_callback_for_calendar_with_new_duty(plugin, calendar, persons)


def enter_update_events_loop(plugin: AbstractPlugin) -> None:
    last_update_check = datetime.now(tz=timezone.utc) - plugin.interval_worker_check_for_update_events
    last_calendar_uid_to_person_id: Dict[str, Union[Set[int], None]] = defaultdict(lambda: None)
    while True:
        if datetime.now(tz=timezone.utc) - last_update_check > plugin.interval_worker_check_for_update_events:
            last_update_check = datetime.now(tz=timezone.utc)

            with create_session() as session:
                calendars_with_new_on_call = get_calendars_with_new_duty(session, last_calendar_uid_to_person_id)
                run_update_event_loop(
                    plugin=plugin, session=session, calendars_with_new_on_call=calendars_with_new_on_call
                )
