import logging
import time
import traceback
from typing import Optional, List

from pendulum import DateTime
from sqlalchemy.orm import Session as SASession, Query

from duty_overview.alchemy.session import create_session
from duty_overview.models.calendar import Calendar
from duty_overview.models.on_call_event import OnCallEvent
from duty_overview.models.person import Person
from duty_overview.plugin.helpers import plugin_fetcher
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


def ensure_person_uniqueness(new_person: Person, session: SASession) -> Person:
    """
    This function ensures we don't have 1000 users with the except same username and or email.
    If there is a new person object with the same username and email, we wipe the old person object and replace the
    UIDS.
    """
    query: Query = (
        session
        .query(Person)
        .filter(Person.uid != new_person.uid)
        .filter(Person.username == new_person.username)
        .filter(Person.email == new_person.email)
    )
    for same_person in query.all():
        logger.warning(f"Deleting {same_person=} in favor of {new_person=}.")
        session.delete(same_person)
        new_values = {"person_uid": new_person.uid}
        session.query(OnCallEvent).filter(OnCallEvent.person_uid == same_person.uid).update(new_values)
        logger.info(f"Also updated all references of {same_person.uid=} to {new_person.uid=} in OnCallEvents table.")
    return new_person


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
                    person = plugin.sync_person(person=person, session=session)
                    person = ensure_person_uniqueness(new_person=person, session=session)
                    person.error_msg = None
                except Exception:
                    logger.exception(f"Failed to update {person}.")
                    person.error_msg = traceback.format_exc()
                finally:
                    person.last_update_utc = DateTime.utcnow()
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
                    calendar = plugin.sync_calendar(calendar=calendar, event_prefix=None, session=session)
                    calendar.error_msg = None
                except Exception:
                    logger.exception(f"Failed to update {calendar}.")
                    calendar.error_msg = traceback.format_exc()
                finally:
                    calendar.last_update_utc = DateTime.utcnow()
            logger.debug(f"Successfully updated {calendar}.")
            time.sleep(1)
    except Exception:
        logger.exception(f"Failed to update {calendar} in the database? Maybe there is some database error?")


def enter_loop():
    # @ToDo(jorrick) sync based on the plugins present.
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()
    while True:
        logger.info("Updating persons.")
        update_all_outdated_persons(plugin=plugin)
        time.sleep(30)
        logger.info("Updating calendars.")
        update_all_outdated_calendars(plugin=plugin)
        time.sleep(30)
