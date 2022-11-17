import logging
import time
import traceback
from typing import Optional

from pendulum import DateTime
from sqlalchemy.orm import Session as SASession

from duty_overview.alchemy.session import create_session
from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person
from duty_overview.plugin import plugin_fetcher
from duty_overview.plugin.abstract_plugin import AbstractPlugin

logger = logging.getLogger(__file__)


def get_most_outdated_person(plugin: AbstractPlugin, session: SASession) -> Optional[Person]:
    update_persons_with_last_update_before: DateTime = DateTime.utcnow() - plugin.person_update_frequency
    return (
        session
        .query(Person)
        .where(Person.last_update_utc <= update_persons_with_last_update_before)
        .order_by(Person.last_update_utc)
        .first()
    )


def get_most_outdated_calendar(plugin: AbstractPlugin, session: SASession) -> Optional[Calendar]:
    update_calendars_with_last_update_before: DateTime = DateTime.utcnow() - plugin.calendar_update_frequency
    return (
        session
        .query(Calendar)
        .where(Calendar.last_update_utc <= update_calendars_with_last_update_before)
        .order_by(Calendar.last_update_utc)
        .first()
    )


def update_all_outdated_persons(plugin: AbstractPlugin) -> None:
    person: Optional[Person] = None
    try:
        while True:
            with create_session() as session:
                person = get_most_outdated_person(plugin=plugin, session=session)
                logger.info(f"Updating {person}.")
                if person is None:
                    break
                try:
                    plugin.sync_person(person=person, session=session)
                except Exception:
                    logger.exception(f"Failed to update {person}.")
                    person.error_msg = traceback.format_exc()
            logger.debug(f"Successfully updated {person}.")
            time.sleep(1)
    except Exception:
        logger.exception(f"Failed to update {person} in the database? Maybe there is some database error?")


def update_all_outdated_calendars(plugin: AbstractPlugin) -> None:
    calendar: Optional[Calendar] = None
    try:
        while True:
            with create_session() as session:
                calendar = get_most_outdated_calendar(plugin=plugin, session=session)
                logger.info(f"Updating {calendar}.")
                if calendar is None:
                    break
                try:
                    plugin.sync_calendar(calendar=calendar, session=session)
                except Exception:
                    logger.exception(f"Failed to update {calendar}.")
                    calendar.error_msg = traceback.format_exc()
            logger.debug(f"Successfully updated {calendar}.")
            time.sleep(1)
    except Exception:
        logger.exception(f"Failed to update {calendar} in the database? Maybe there is some database error?")


def enter_loop():
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()
    while True:
        logger.info("Updating persons.")
        update_all_outdated_persons(plugin=plugin)
        time.sleep(30)
        logger.info("Updating calendars.")
        update_all_outdated_calendars(plugin=plugin)
        time.sleep(30)
