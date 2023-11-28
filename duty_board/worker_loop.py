import logging
import time
import traceback
from typing import Optional, Sequence, Tuple

from pendulum.datetime import DateTime
from sqlalchemy import Select, Update, or_, select, update
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.plugin.abstract_plugin import AbstractPlugin

logger = logging.getLogger(__name__)


def get_most_outdated_person(plugin: AbstractPlugin, session: SASession) -> Optional[Person]:
    update_persons_with_last_update_before: DateTime = DateTime.utcnow() - plugin.person_update_frequency
    stmt = (
        select(Person)
        .where(Person.last_update_utc <= update_persons_with_last_update_before)
        .order_by(Person.last_update_utc)
        .limit(1)
    )
    return session.scalar(stmt)


def get_most_outdated_calendar(plugin: AbstractPlugin, session: SASession) -> Optional[Calendar]:
    update_calendars_with_last_update_before: DateTime = DateTime.utcnow() - plugin.calendar_update_frequency
    stmt: Select[Tuple[Calendar]] = (
        select(Calendar)
        .where(Calendar.last_update_utc <= update_calendars_with_last_update_before)
        .order_by(Calendar.last_update_utc)
        .limit(1)
    )
    return session.scalar(stmt)


def ensure_person_uniqueness(new_person: Person) -> Person:
    """
    This function ensures we don't have 1000 users with the except same username and or email.
    If there is a new person object with the same username and email, we wipe the old person object and replace the
    UIDS. This requires to be done in a separate session to prevent duplicate key issues.
    """
    extra_session: SASession
    with create_session() as extra_session:
        # Required to expunge, otherwise the commit will also update new_person and will raise a DuplicateKeyIndexError.
        extra_session.expunge(new_person)
        query: Select[Tuple[Person]] = select(Person).where(Person.uid != new_person.uid)
        if new_person.username and new_person.email:
            query = query.where(or_(Person.username == new_person.username, Person.email == new_person.email))
        elif new_person.username:
            query = query.where(Person.username == new_person.username)
        elif new_person.email:
            query = query.where(Person.email == new_person.email)
        else:
            raise ValueError(f"{new_person.uid=} has both {new_person.username=} and {new_person.email=} as None.")

        result: Sequence[Person] = extra_session.scalars(query).all()
        logger.debug(f"Found {len(result)=}, {result=}.")

        for same_person in result:
            logger.info(f"Updating all references of {same_person.uid=} to {new_person.uid=} in OnCallEvents table.")
            # Does this need to be executed somehow?
            stmt: Update = (
                update(OnCallEvent).where(OnCallEvent.person_uid == same_person.uid).values(person_uid=new_person.uid)
            )
            extra_session.execute(stmt)
            logger.warning(f"Deleting {same_person.uid=} {same_person=} in favor of {new_person.uid=} {new_person=}.")
            extra_session.delete(same_person)
            extra_session.commit()
    return new_person


def update_the_most_outdated_person(plugin: AbstractPlugin) -> None:
    try:
        with create_session() as session:
            person: Optional[Person]
            if (person := get_most_outdated_person(plugin=plugin, session=session)) is None:
                logger.debug("Nothing to update here :).")
                time.sleep(1)  # Avoid overload on the database.
                return

            logger.info(f"Updating {person=}.")
            try:
                person = plugin.sync_person(person=person, session=session)
                logger.debug(f"Successfully executed plugins sync_person() for {person=}.")
                person = ensure_person_uniqueness(new_person=person)
                person.error_msg = None
            except Exception:
                logger.exception(f"Failed to update {person=}.")
                person.error_msg = traceback.format_exc()
            finally:
                person.last_update_utc = DateTime.utcnow()
                session.merge(person)
        logger.info("Successfully updated the state of the person in the database.")
    except Exception:
        logger.exception("Failed to update a person in the database. There is probably some database error.")


def update_the_most_outdated_calendar(plugin: AbstractPlugin) -> None:
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
                logger.exception(f"Failed to update {calendar=}.")
                calendar.error_msg = traceback.format_exc()
            finally:
                calendar.last_update_utc = DateTime.utcnow()
                session.merge(calendar)
        logger.info("Successfully updated the state of the calendar in the database.")
    except Exception:
        logger.exception("Failed to update some calendar in the database. There is probably some database error.")


def enter_calendar_refresher_loop(plugin: AbstractPlugin) -> None:
    while True:
        update_the_most_outdated_calendar(plugin=plugin)


def enter_duty_officer_refresher_loop(plugin: AbstractPlugin) -> None:
    while True:
        update_the_most_outdated_person(plugin=plugin)
