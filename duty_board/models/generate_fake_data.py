import json
import random
from datetime import timedelta
from typing import List

from pendulum import DateTime
from sqlalchemy.orm import Session as SASession

from duty_board.alchemy.session import provide_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person


@provide_session
def create_calendars(session: SASession) -> None:
    nr_1 = Calendar(
        uid="data_platform_duty",
        name="Data Platform Duty",
        description="If you have any issues with Spark, Airflow or Jupyterhub, contact these guys. "
        "They are available 24/7, however, they work in AMS hours. Only call them if there is an "
        "emergency.",
        category="Big Data",
        order=1,
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    nr_2 = Calendar(
        uid="infrastructure_duty",
        name="Infrastructure",
        description="If you have any issues with Firewalls or critical tools such as Yarn, HDFS etc."
        "However, usually Data Platform Duty is your first point of contact for application "
        "issues.",
        category="Infrastructure",
        order=2,
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    nr_3 = Calendar(
        uid="machine_learning",
        name="Machine learning",
        description="Do you have any issues with your machine learning tools? Ask these guys.",
        category="Big Data",
        order=3,
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    session.merge(nr_1)
    session.merge(nr_2)
    session.merge(nr_3)


@provide_session
def create_persons(session: SASession) -> None:
    nr_1 = Person(
        username="jorrick",
        email="jorricks@gmail.com",
        img_filename="bert.jpeg",
        extra_attributes_json=json.dumps(
            {
                "mattermost": {
                    "information": "Send Mattermost message",
                    "icon": "FaExchangeAlt",
                    "icon_color": "#2980B9",
                    "url": "https://mattermost.com/jorrick",
                },
            }
        ),
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    nr_2 = Person(
        username="bart",
        email="bart@gmail.com",
        img_filename="bert.jpeg",
        extra_attributes_json=json.dumps(
            {
                "mattermost": {
                    "information": "Send Mattermost message",
                    "icon": "FaExchangeAlt",
                    "icon_color": "#2980B9",
                    "url": "https://mattermost.com/bart",
                },
            }
        ),
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    session.merge(nr_1)
    session.merge(nr_2)


@provide_session
def create_on_call_events(person_uids: List[int], session: SASession) -> None:
    items_to_add = []
    for calendar_uid in ["data_platform_duty", "infrastructure_duty", "machine_learning"]:
        nr_1 = OnCallEvent(
            calendar_uid=calendar_uid,
            start_event_utc=DateTime.utcnow(),
            end_event_utc=DateTime.utcnow() + timedelta(days=1),
            person_uid=random.choice(person_uids),
        )
        nr_2 = OnCallEvent(
            calendar_uid=calendar_uid,
            start_event_utc=DateTime.utcnow() + timedelta(days=1),
            end_event_utc=DateTime.utcnow() + timedelta(days=2),
            person_uid=random.choice(person_uids),
        )
        nr_3 = OnCallEvent(
            calendar_uid=calendar_uid,
            start_event_utc=DateTime.utcnow() + timedelta(days=2),
            end_event_utc=DateTime.utcnow() + timedelta(days=4),
            person_uid=random.choice(person_uids),
        )
        nr_4 = OnCallEvent(
            calendar_uid=calendar_uid,
            start_event_utc=DateTime.utcnow() + timedelta(days=4),
            end_event_utc=DateTime.utcnow() + timedelta(days=5),
            person_uid=random.choice(person_uids),
        )
        items_to_add.extend([nr_1, nr_2, nr_3, nr_4])
    session.bulk_save_objects(items_to_add)


@provide_session
def create_fake_database_rows_if_not_present(session: SASession) -> None:
    if session.query(Calendar).count() < 3:
        create_calendars()
    if session.query(Person).count() < 2:
        create_persons()
    person_uids = [uid[0] for uid in session.query(Person).values(Person.uid)]
    if session.query(OnCallEvent).count() < 5:
        create_on_call_events(person_uids)
