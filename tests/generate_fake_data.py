import json
import random
from datetime import timedelta
from typing import List

from pendulum.datetime import DateTime
from pendulum.tz.timezone import Timezone
from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person

UPDATE_TIME = DateTime(2023, 11, 28, 11, 46, 6, 0, tzinfo=Timezone("UTC"))


def create_calendars(session: SASession) -> List[Calendar]:
    all_calenders: List[Calendar] = [
        Calendar(
            uid="data_platform_duty",
            name="Data Platform Duty",
            description="If you have any issues with Spark, Airflow or Jupyterhub, contact these guys. "
            "They are available 24/7, however, they work in AMS hours. Only call them if there is an "
            "emergency.",
            icalendar_url="https://non-existing-endpoint1.com",
            category="Big Data",
            order=1,
            last_update_utc=UPDATE_TIME,
            sync=False,
        ),
        Calendar(
            uid="infrastructure_duty",
            name="Infrastructure",
            description="If you have any issues with Firewalls or critical tools such as Yarn, HDFS etc."
            "However, usually Data Platform Duty is your first point of contact for application "
            "issues.",
            icalendar_url="https://non-existing-endpoint2.com",
            category="Infrastructure",
            order=2,
            last_update_utc=UPDATE_TIME,
            sync=False,
        ),
        Calendar(
            uid="machine_learning",
            name="Machine learning",
            description="Do you have any issues with your machine learning tools? Ask these guys.",
            icalendar_url="https://non-existing-endpoint3.com",
            category="Big Data",
            order=3,
            last_update_utc=UPDATE_TIME,
            sync=False,
        ),
    ]
    session.add_all(all_calenders)
    session.flush(all_calenders)
    return all_calenders


def create_persons(session: SASession) -> List[Person]:
    all_persons: List[Person] = [
        Person(
            username="jorrick",
            email="some_email@gmail.com",
            image=None,
            img_width=None,
            img_height=None,
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
            last_update_utc=UPDATE_TIME,
            sync=False,
        ),
        Person(
            username="bart",
            email="bart@gmail.com",
            image=None,
            img_width=None,
            img_height=None,
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
            last_update_utc=UPDATE_TIME,
            sync=False,
        ),
    ]
    session.add_all(all_persons)
    session.flush(all_persons)
    return all_persons


def create_on_call_events(calendars: List[Calendar], persons: List[Person], session: SASession) -> None:
    items_to_add = []
    for calendar in calendars:
        nr_1 = OnCallEvent(
            calendar=calendar,
            start_event_utc=UPDATE_TIME,
            end_event_utc=UPDATE_TIME + timedelta(days=1),
            person=random.choice(persons),
        )
        nr_2 = OnCallEvent(
            calendar=calendar,
            start_event_utc=UPDATE_TIME + timedelta(days=1),
            end_event_utc=UPDATE_TIME + timedelta(days=2),
            person=random.choice(persons),
        )
        nr_3 = OnCallEvent(
            calendar=calendar,
            start_event_utc=UPDATE_TIME + timedelta(days=2),
            end_event_utc=UPDATE_TIME + timedelta(days=4),
            person=random.choice(persons),
        )
        nr_4 = OnCallEvent(
            calendar=calendar,
            start_event_utc=UPDATE_TIME + timedelta(days=4),
            end_event_utc=UPDATE_TIME + timedelta(days=5),
            person=random.choice(persons),
        )
        items_to_add.extend([nr_1, nr_2, nr_3, nr_4])
    session.add_all(items_to_add)
    session.flush(items_to_add)


def create_fake_database_rows_if_not_present(session: SASession) -> None:
    calendars: List[Calendar] = create_calendars(session)
    persons: List[Person] = create_persons(session)
    create_on_call_events(calendars, persons, session)
