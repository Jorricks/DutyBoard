import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, List

import pytest
from pendulum.tz.timezone import UTC
from sqlalchemy import delete
from sqlalchemy.orm.session import Session as SASession

from duty_board.alchemy import settings
from duty_board.alchemy.session import create_session
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.models.person_image import PersonImage
from duty_board.models.token import Token
from duty_board.plugin.example.example_plugin import ExamplePlugin
from tests import generate_fake_data

os.environ["LDAP_FULL_QUANTIFIED_USERNAME"] = "cn=admin,dc=DutyBoard,dc=com"
os.environ["LDAP_PASSWORD"] = "adminpassword"  # noqa: S105


@pytest.fixture(scope="session", autouse=True)
def _auto_kill_docker_refreshers() -> None:
    # We kill the docker containers that would automatically refresh stuff in the background.
    containers_to_kill: List[str] = ["duty_worker_calendar", "duty_worker_persons"]
    if docker_path := shutil.which("docker"):
        subprocess.run([docker_path, "stop", *containers_to_kill])  # noqa: PLW1510, S603


@contextmanager
def set_ldap_env_variables() -> Generator[None, None, None]:
    try:
        os.environ["LDAP_FULL_QUANTIFIED_USERNAME"] = "cn=admin,dc=DutyBoard,dc=com"
        os.environ["LDAP_PASSWORD"] = "adminpassword"  # noqa: S105
        yield None
    finally:
        if "LDAP_FULL_QUANTIFIED_USERNAME" in os.environ:
            del os.environ["LDAP_FULL_QUANTIFIED_USERNAME"]
        if "LDAP_PASSWORD" in os.environ:
            del os.environ["LDAP_PASSWORD"]


@contextmanager
def get_loaded_ldap_plugin() -> Generator[ExamplePlugin, None, None]:
    with set_ldap_env_variables():
        yield ExamplePlugin()


@pytest.fixture()
def _wipe_database() -> None:
    session = settings.Session()
    session.execute(delete(Calendar))
    session.execute(delete(OnCallEvent))
    session.execute(delete(Person))
    session.execute(delete(PersonImage))
    session.execute(delete(Token))


@pytest.fixture()
def set_up_persons(_wipe_database: None) -> List[Person]:
    session: SASession
    with create_session() as session:
        persons = [
            Person(
                username="jan",
                email="jan@schoenmaker.nl",
                extra_attributes_json=json.dumps(
                    {
                        "fullName": {"information": "Jan Schoenmakers", "icon": "FaUserCircle"},
                        "location": {"information": "Amsterdam, NL", "icon": "FaMapMarkerAlt"},
                    }
                ),
                img_height=640,
                img_width=428,
                image=PersonImage(
                    image_in_bytes=(Path(__file__).parent / "data" / "openldap_ldifs" / "jan.jpeg").read_bytes()
                ),
                last_update_utc=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
            ),
            Person(
                username="henk",
                email="henk@tank.nl",
                extra_attributes_json=json.dumps(
                    {
                        "fullName": {"information": "Henk de Tank", "icon": "FaUserCircle"},
                        "location": {"information": "Eindhoven de gekste, NL", "icon": "FaMapMarkerAlt"},
                    }
                ),
                img_height=805,
                img_width=736,
                image=PersonImage(
                    image_in_bytes=(Path(__file__).parent / "data" / "openldap_ldifs" / "henk.jpeg").read_bytes()
                ),
                last_update_utc=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC),
            ),
        ]
        session.add_all(persons)

    return persons


@pytest.fixture()
def _get_fake_dataset(_wipe_database: None) -> None:
    with create_session() as session:
        generate_fake_data.create_fake_database_rows_if_not_present(session)
