from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session as SASession
from starlette.testclient import TestClient

from duty_board.alchemy.session import create_session
from duty_board.models.person import Person
from duty_board.models.person_image import PersonImage
from duty_board.server import app


@pytest.mark.usefixtures("_get_fake_dataset")
def test_get_schedule() -> None:
    client = TestClient(app)
    result = client.get("/schedule", params={"timezone": "Europe/Amsterdam"})
    result_json = result.json()
    assert result_json["config"] == {
        "timezone": "Europe/Amsterdam",
        "text_color": "white",
        "background_color": "#3C9C2D",
        "categories": ["Big Data", "Infrastructure"],
        "git_repository_url": "https://github.com/Jorricks/DutyBoard",
        "enable_admin_button": False,
        "announcement_text_color": "#FFFFFF",
        "announcement_background_color": "#FF0000",
        "announcements": [
            "This is a debug setup. Please disable this announcement in your plugin by overwriting announcements variable."
        ],
        "footer_html": '\n    Welcome to DutyBoard. <br>\n    In case you want to know more check <a href="https://github.com/Jorricks/DutyBoard">here</a>.<br>\n    Cheers!\n    ',
    }

    assert len(result_json["calendars"]) == 3
    assert result_json["calendars"][0]["uid"] == "data_platform_duty"
    assert result_json["calendars"][0]["name"] == "Data Platform Duty"
    assert (
        result_json["calendars"][0]["description"]
        == "If you have any issues with Spark, Airflow or Jupyterhub, contact these guys. They are available 24/7, however, they work in AMS hours. Only call them if there is an emergency."
    )
    assert result_json["calendars"][0]["category"] == "Big Data"
    assert result_json["calendars"][0]["order"] == 1
    assert result_json["calendars"][0]["error_msg"] == ""
    assert result_json["calendars"][0]["sync"] is False
    assert len(result_json["calendars"][0]["events"]) == 4
    assert result_json["calendars"][0]["events"][0]["start_event"] == "2023-11-28 12:46:06 CET"
    assert result_json["calendars"][0]["events"][0]["end_event"] == "2023-11-29 12:46:06 CET"
    assert result_json["calendars"][0]["events"][1]["start_event"] == "2023-11-29 12:46:06 CET"
    assert result_json["calendars"][0]["events"][1]["end_event"] == "2023-11-30 12:46:06 CET"
    assert result_json["calendars"][0]["events"][2]["start_event"] == "2023-11-30 12:46:06 CET"
    assert result_json["calendars"][0]["events"][2]["end_event"] == "2023-12-02 12:46:06 CET"
    assert result_json["calendars"][0]["events"][3]["start_event"] == "2023-12-02 12:46:06 CET"
    assert result_json["calendars"][0]["events"][3]["end_event"] == "2023-12-03 12:46:06 CET"

    assert len(result_json["persons"]) == 2
    person_values = list(result_json["persons"].values())
    assert person_values[0]["username"] == "jorrick"
    assert person_values[0]["email"] == "some_email@gmail.com"
    assert person_values[1]["username"] == "bart"
    assert person_values[1]["email"] == "bart@gmail.com"
    uids = list(result_json["persons"].keys())
    assert result_json["persons"][uids[0]]["uid"] == int(uids[0])
    assert result_json["persons"][uids[1]]["uid"] == int(uids[1])


@pytest.mark.usefixtures("_get_fake_dataset")
def test_get_person() -> None:
    client = TestClient(app)
    session: SASession
    with create_session() as session:
        person: Person = session.scalars(select(Person).where(Person.username == "bart")).one()
    result = client.get("/person", params={"person_uid": person.uid, "timezone": "Europe/Amsterdam"})
    result_json = result.json()
    assert result_json["uid"] == person.uid
    assert result_json["username"] == "bart"
    assert result_json["email"] == "bart@gmail.com"
    assert result_json["img_filename"] is None
    assert result_json["img_width"] is None
    assert result_json["img_height"] is None
    assert result_json["extra_attributes"] == [
        {
            "information": "Send Mattermost message",
            "icon": "FaExchangeAlt",
            "icon_color": "#2980B9",
            "url": "https://mattermost.com/bart",
        }
    ]
    assert result_json["last_update"] == "2023-11-28 12:46:06 CET"
    assert result_json["error_msg"] == ""
    assert result_json["sync"] is False


@pytest.mark.usefixtures("_wipe_database")
def test_empty_persons_table() -> None:
    client = TestClient(app)
    with pytest.raises(ValueError, match="Invalid person_uid=0 passed."):
        client.get("/person", params={"person_uid": 0, "timezone": "Europe/Amsterdam"})


@pytest.mark.usefixtures("_wipe_database")
def test_get_person_image() -> None:
    client = TestClient(app)
    session: SASession
    with create_session() as session:
        person_image = PersonImage(
            image_in_bytes=(Path(__file__).parent / "data" / "openldap_ldifs" / "jan.jpeg").read_bytes()
        )
        session.add(person_image)

    with pytest.raises(NoResultFound, match="No row was found when one was required"):
        client.get("/person_img/999999999")

    response = client.get(f"/person_img/{person_image.uid}")
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == person_image.image_in_bytes
