import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Optional, Tuple

from pendulum.datetime import DateTime
from prometheus_client import Counter, Gauge
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.plugin.abstract_plugin import AbstractPlugin

logger = logging.getLogger(__name__)

calendars_gauge = Gauge("duty_calendar_amount", "Number of calendars listed in the database.")
calendars_outdated_gauge = Gauge("duty_calendars_outdated_amount", "Number of calendars that require an update.")
calendars_errors_gauge = Gauge("duty_calendars_errors_amount", "Number of calendars that have errors.")
calendar_refresh_run_counter = Counter("duty_calendars_refresh_counter", "Count the number of calendar refresh runs.")
calendar_refresh_run_success_counter = Counter(
    "duty_calendars_refresh_success_counter", "Count the number of calendar refresh runs that succeed."
)
calendar_refresh_run_failed_counter = Counter(
    "duty_calendars_refresh_failed_counter", "Count the number of calendar refresh runs that fail."
)
calendar_refresh_failed = Gauge(
    "duty_calendars_last_refresh_failed", "Indicate whether the last refresh failed", ["calendar_name"]
)


def get_most_outdated_calendar(plugin: AbstractPlugin, session: SASession) -> Optional[Calendar]:
    update_calendars_with_last_update_before: DateTime = DateTime.utcnow() - plugin.calendar_update_frequency
    stmt: Select[Tuple[Calendar]] = (
        select(Calendar)
        .where(Calendar.last_update_utc <= update_calendars_with_last_update_before)
        .order_by(Calendar.last_update_utc)
        .limit(1)
    )
    return session.scalar(stmt)


def update_the_most_outdated_calendar(plugin: AbstractPlugin) -> None:
    calendar_refresh_run_counter.inc()
    failed: bool = False
    try:
        with create_session() as session:
            calendar: Optional[Calendar]
            if (calendar := get_most_outdated_calendar(plugin=plugin, session=session)) is None:
                logger.debug("Nothing to update here :).")
                time.sleep(1)  # Avoid overload on the database.
                return

            logger.info(f"Updating {calendar=}.")
            try:
                calendar = plugin.sync_calendar(calendar=calendar, session=session)
                logger.debug(f"Successfully executed plugins sync_calendar() for {calendar=}.")
                calendar.error_msg = None
            except Exception:
                failed = True
                logger.exception(f"Failed to update {calendar=}.")
                calendar.error_msg = traceback.format_exc()
            finally:
                calendar.last_update_utc = DateTime.utcnow()
                session.merge(calendar)
        logger.info("Successfully updated the state of the calendar in the database.")
    except Exception:
        failed = True
        logger.exception("Failed to update some calendar in the database. There is probably some database error.")

    if calendar is not None:
        calendar_refresh_failed.labels(calendar.name).set(int(failed))
    if failed:
        calendar_refresh_run_failed_counter.inc()
    else:
        calendar_refresh_run_success_counter.inc()


def collect_extra_metrics_calendar(plugin: AbstractPlugin) -> None:
    logger.info("Updating calender metrics.")
    with create_session() as session:
        number_of_calendars: int = session.scalar(select(func.count(Calendar.uid)))  # type: ignore[assignment]
        calendars_gauge.set(number_of_calendars)

        update_calendars_with_last_update_before: DateTime = DateTime.utcnow() - plugin.calendar_update_frequency
        number_of_out_dated_calendars: int = session.scalar(  # type: ignore[assignment]
            select(func.count(Calendar.uid)).where(Calendar.last_update_utc <= update_calendars_with_last_update_before)
        )
        calendars_outdated_gauge.set(number_of_out_dated_calendars)

        number_of_calendars_with_errors: int = session.scalar(  # type: ignore[assignment]
            select(func.count(Calendar.uid)).where(Calendar.error_msg != None)  # noqa: E711
        )
        calendars_errors_gauge.set(number_of_calendars_with_errors)


def enter_calendar_refresher_loop(plugin: AbstractPlugin) -> None:
    last_metrics_update = datetime.now(tz=timezone.utc) - plugin.interval_worker_metrics_update
    while True:
        if datetime.now(tz=timezone.utc) - last_metrics_update > plugin.interval_worker_metrics_update:
            collect_extra_metrics_calendar(plugin=plugin)
            last_metrics_update = datetime.now(tz=timezone.utc)

        update_the_most_outdated_calendar(plugin=plugin)
