import json
from pathlib import Path

import pytest

from duty_board.alchemy import settings
from duty_board.models.person import Person
from duty_board.plugin.example.example_plugin import ExamplePlugin
from tests.conftest import get_loaded_ldap_plugin


def verify_jan_got_filled_correctly(person: Person) -> None:
    assert person.username == "jan"
    assert person.email == "jan@schoenmaker.nl"
    extra_attributes_json = person.extra_attributes_json
    assert extra_attributes_json is not None
    person_attributes = json.loads(extra_attributes_json)
    assert person_attributes["fullName"]["information"] == "Jan Schoenmakers"
    assert person_attributes["location"]["information"] == "Amsterdam, NL"
    assert person.img_height == 640
    assert person.img_width == 428
    location_to_jans_image = Path(__file__).parent.parent / "data" / "openldap_ldifs" / "jan.jpeg"
    person_image = person.image
    assert person_image is not None
    assert person_image.image_in_bytes == location_to_jans_image.read_bytes()


def test_sync_person() -> None:
    plugin: ExamplePlugin
    with get_loaded_ldap_plugin() as plugin:
        person = Person(username="jan")
        person = plugin.sync_person(person=person, session=settings.Session())
        verify_jan_got_filled_correctly(person)

        person = Person(email="jan@schoenmaker.nl")
        person = plugin.sync_person(person=person, session=settings.Session())
        verify_jan_got_filled_correctly(person)


@pytest.mark.asyncio()
async def test_admin_login_attempt() -> None:
    with get_loaded_ldap_plugin() as plugin:
        assert await plugin.admin_login_attempt("jan", "") is True
        assert await plugin.admin_login_attempt("henk", "") is False
        assert await plugin.admin_login_attempt("non-existing", "") is False
