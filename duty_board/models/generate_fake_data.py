import json
import random
from datetime import timedelta
from typing import List

from pendulum.datetime import DateTime
from sqlalchemy import func, select
from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person


def create_calendars(session: SASession) -> List[Calendar]:
    nr_1 = Calendar(
        uid="data_platform_duty",
        name="Data Platform Duty",
        description="If you have any issues with Spark, Airflow or Jupyterhub, contact these guys. "
        "They are available 24/7, however, they work in AMS hours. Only call them if there is an "
        "emergency.",
        icalendar_url="https://non-existing-endpoint1.com",
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
        icalendar_url="https://non-existing-endpoint2.com",
        category="Infrastructure",
        order=2,
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    nr_3 = Calendar(
        uid="machine_learning",
        name="Machine learning",
        description="Do you have any issues with your machine learning tools? Ask these guys.",
        icalendar_url="https://non-existing-endpoint3.com",
        category="Big Data",
        order=3,
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    session.merge(nr_1)
    session.merge(nr_2)
    session.merge(nr_3)
    return [nr_1, nr_2, nr_3]


def create_persons(session: SASession) -> None:
    nr_1 = Person(
        username="jorrick",
        email="jorricks@gmail.com",
        img_filename="bert.jpeg",
        img_width=3000,
        img_height=2000,
        extra_attributes_json=json.dumps(
            {
                "mattermost": {
                    "information": "Send Mattermost message",
                    "icon": "FaExchangeAlt",
                    "icon_color": "#2980B9",
                    "url": "https://mattermost.com/jorrick",
                },
            },
        ),
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    nr_2 = Person(
        username="bart",
        email="bart@gmail.com",
        img_filename="bert2.jpg",
        img_width=900,
        img_height=1180,
        extra_attributes_json=json.dumps(
            {
                "mattermost": {
                    "information": "Send Mattermost message",
                    "icon": "FaExchangeAlt",
                    "icon_color": "#2980B9",
                    "url": "https://mattermost.com/bart",
                },
            },
        ),
        last_update_utc=DateTime.utcnow(),
        sync=False,
    )
    session.merge(nr_1)
    session.merge(nr_2)


def create_on_call_events(calendars: List[Calendar], persons: List[Person], session: SASession) -> None:
    items_to_add = []
    for calendar in calendars:
        nr_1 = OnCallEvent(
            calendar=calendar,
            start_event_utc=DateTime.utcnow(),
            end_event_utc=DateTime.utcnow() + timedelta(days=1),
            person=random.choice(persons),
        )
        nr_2 = OnCallEvent(
            calendar=calendar,
            start_event_utc=DateTime.utcnow() + timedelta(days=1),
            end_event_utc=DateTime.utcnow() + timedelta(days=2),
            person=random.choice(persons),
        )
        nr_3 = OnCallEvent(
            calendar=calendar,
            start_event_utc=DateTime.utcnow() + timedelta(days=2),
            end_event_utc=DateTime.utcnow() + timedelta(days=4),
            person=random.choice(persons),
        )
        nr_4 = OnCallEvent(
            calendar=calendar,
            start_event_utc=DateTime.utcnow() + timedelta(days=4),
            end_event_utc=DateTime.utcnow() + timedelta(days=5),
            person=random.choice(persons),
        )
        items_to_add.extend([nr_1, nr_2, nr_3, nr_4])
    session.bulk_save_objects(items_to_add)


def create_fake_database_rows_if_not_present(session: SASession) -> None:
    if session.query(func.count(Calendar.uid)).scalar() < 3:
        create_calendars(session)
    if session.query(func.count(Person.uid)).scalar() < 2:
        create_persons(session)
    calendars: List[Calendar] = list(session.scalars(select(Calendar)).all())
    persons: List[Person] = list(session.scalars(select(Person)).all())
    if session.query(func.count(OnCallEvent.uid)).scalar() < 5:
        create_on_call_events(calendars, persons, session)
