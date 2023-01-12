import logging
import time
import traceback
from typing import Optional

from pendulum import DateTime
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy import queries, settings
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.helpers import plugin_fetcher

logger = logging.getLogger(__name__)


def get_most_outdated_person(plugin: AbstractPlugin, session: SASession) -> Optional[Person]:
    update_persons_with_last_update_before: DateTime = DateTime.utcnow() - plugin.person_update_frequency
    return (
        session.query(Person)
        .where(Person.last_update_utc <= update_persons_with_last_update_before)
        .order_by(Person.last_update_utc)
        .first()
    )


def get_most_outdated_calendar(plugin: AbstractPlugin, session: SASession) -> Optional[Calendar]:
    update_calendars_with_last_update_before: DateTime = DateTime.utcnow() - plugin.calendar_update_frequency
    return (
        session.query(Calendar)
        .where(Calendar.last_update_utc <= update_calendars_with_last_update_before)
        .order_by(Calendar.last_update_utc)
        .first()
    )


def ensure_person_uniqueness(new_person: Person) -> Person:
    """
    This function ensures we don't have 1000 users with the except same username and or email.
    If there is a new person object with the same username and email, we wipe the old person object and replace the
    UIDS. This requires to be done in a separate session to prevent duplicate key issues.
    """
    with create_session() as extra_session:
        # Required to expunge, otherwise the commit will also update new_person and will raise a DuplicateKeyIndexError.
        extra_session.expunge(new_person)
        query: Query = extra_session.query(Person).filter(Person.uid != new_person.uid)
        if new_person.username and new_person.email:
            query = query.filter(or_(Person.username == new_person.username, Person.email == new_person.email))
        elif new_person.username:
            query = query.filter(Person.username == new_person.username)
        elif new_person.email:
            query = query.filter(Person.email == new_person.email)
        else:
            raise ValueError(f"{new_person.uid=} has both {new_person.username=} and {new_person.email=} as None.")

        result = query.all()
        logger.debug(f"Found {len(result)=}, {result=}.")

        for same_person in result:
            logger.info(f"Updating all references of {same_person.uid=} to {new_person.uid=} in OnCallEvents table.")
            new_values = {"person_uid": new_person.uid}
            extra_session.query(OnCallEvent).filter(OnCallEvent.person_uid == same_person.uid).update(new_values)
            logger.warning(f"Deleting {same_person.uid=} {same_person=} in favor of {new_person.uid=} {new_person=}.")
            extra_session.delete(same_person)
            extra_session.commit()
    return new_person


def update_all_outdated_persons(plugin: AbstractPlugin) -> None:
    person: Optional[Person] = None
    while True:
        with create_session() as session:
            try:
                person = get_most_outdated_person(plugin=plugin, session=session)
                if person is None:
                    logger.debug("Nothing to update here :).")
                    break
                logger.info(f"Updating {person}.")
                try:
                    person = plugin.sync_person(person=person, session=session)
                    logger.debug("Successfully executed plugins sync_person().")
                    person = ensure_person_uniqueness(new_person=person)
                    person.error_msg = None
                except Exception:
                    logger.exception(f"Failed to update {person}.")
                    person.error_msg = traceback.format_exc()
                finally:
                    person.last_update_utc = DateTime.utcnow()
                    session.merge(person)
            except Exception:
                logger.exception(f"Failed to update {person} in the database? Maybe there is some database error?")
        logger.info("Successfully finished updating person.")


def update_all_outdated_calendars(plugin: AbstractPlugin) -> None:
    calendar: Optional[Calendar] = None
    for _ in range(3):  # Update at most x calendars before we resort to updating persons.
        with create_session() as session:
            try:
                calendar = get_most_outdated_calendar(plugin=plugin, session=session)
                if calendar is None:
                    logger.debug("Nothing to update here :).")
                    break
                logger.info(f"Updating {calendar}.")
                try:
                    calendar = plugin.sync_calendar(calendar=calendar, session=session)
                    logger.debug("Successfully executed plugins sync_calendar().")
                    calendar.error_msg = None
                except Exception:
                    logger.exception(f"Failed to update {calendar}.")
                    calendar.error_msg = traceback.format_exc()
                finally:
                    calendar.last_update_utc = DateTime.utcnow()
                    session.merge(calendar)
                logger.debug(f"Successfully updated {calendar}.")
            except Exception:
                logger.exception(f"Failed to update {calendar} in the database? Maybe there is some database error?")
        logger.info("Successfully finished updating calendar.")


def enter_loop():
    settings.configure_orm()
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()

    logger.info("Updating plugin calendars in the database.")
    with create_session() as session:
        queries.sync_duty_calendar_configurations_to_postgres(session, plugin.duty_calendar_configurations)

    while True:
        try:
            logger.info("Starting another update pass.")
            update_all_outdated_calendars(plugin=plugin)
            time.sleep(1)
            update_all_outdated_persons(plugin=plugin)
            time.sleep(1)
        except SQLAlchemyError:
            logger.exception("Error occurred when updating the database.")
            time.sleep(1)
