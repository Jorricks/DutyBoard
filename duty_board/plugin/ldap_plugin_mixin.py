import asyncio
import io
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from PIL import Image
from sqlalchemy.orm import Session as SASession

from duty_board.models.person import Person
from duty_board.models.person_image import PersonImage
from duty_board.plugin.helpers.ldap_helper import LDAPBaseClient

logger = logging.getLogger(__name__)


class LDAPPluginMixin:
    # Basic LDAP settings
    LDAP_URL: ClassVar[str] = os.environ.get("LDAP_URL", "ldap://127.0.0.1:1389")
    LDAP_BASE_DN: ClassVar[str] = "dc=DutyBoard,dc=com"
    LDAP_USER_OU: ClassVar[str] = "People"
    LDAP_GROUP_OU: ClassVar[Optional[str]] = "Groups"
    LDAP_ACCOUNT_ATTRIBUTE: ClassVar[str] = "uid"
    LDAP_GROUP_ATTRIBUTE: ClassVar[str] = "cn"
    # Group would be cn=a_group,ou=Group,dc=example,dc=com
    # With the above config you'd have:
    # - Users -> `uid=abc,ou=People,dc=example,dc=com` = f'{ACCOUNT_ATTRIBUTE}=abc,ou={LDAP_USER_OU},{LDAP_BASE_DN}'.
    # - Groups -> `cn=folks,ou=Group,dc=example,dc=com` = f'{GROUP_ATTRIBUTE}=folks,ou={LDAP_GROUP_OU},{LDAP_BASE_DN}'

    # To configure who gets access to the admin interface.
    # This can either be `"groupOfUniqueNames", "uniquemember"` or `"groupOfNames", `member`
    LDAP_GROUP_MEMBERSHIP_RELATION: ClassVar[Tuple[str, str]] = "groupOfUniqueNames", "uniquemember"
    # Allow everyone part of `cn=admin-unique-interface,ou=Group,dc=DutyBoard,dc=com` to login to the admin interface.
    LDAP_ADMIN_GROUP_NAMES: ClassVar[Tuple[str, ...]] = ("admin-unique-interface",)

    def __init__(self, *args: Any, **kwargs: Any):
        self.client: Optional[LDAPBaseClient] = None
        super().__init__(*args, **kwargs)

    def get_client(self) -> LDAPBaseClient:
        if self.client is not None:
            return self.client
        self.client = LDAPBaseClient(
            url=self.LDAP_URL,
            base_dn=self.LDAP_BASE_DN,
            user_organizational_unit=self.LDAP_USER_OU,
            group_organizational_unit=self.LDAP_GROUP_OU,
            account_attribute=self.LDAP_ACCOUNT_ATTRIBUTE,
            group_attribute=self.LDAP_GROUP_ATTRIBUTE,
            ldap_group_membership_relation=self.LDAP_GROUP_MEMBERSHIP_RELATION,
            full_quantified_username=os.environ["LDAP_FULL_QUANTIFIED_USERNAME"],
            password=os.environ["LDAP_PASSWORD"],
            auto_referrals=False,
        )
        return self.client

    @staticmethod
    def _get_jpeg_photo_from_person(
        person_attributes: Mapping[str, Union[str, List[str]]],
    ) -> Optional[Tuple[bytes, int, int]]:
        if "jpegPhoto" not in person_attributes:
            return None
        img_as_b64: bytes = person_attributes["jpegPhoto"][0]  # type: ignore
        image = Image.open(io.BytesIO(img_as_b64))
        return img_as_b64, image.width, image.height

    def _extract_user_info(self, username: str) -> Tuple[str, Mapping[str, Union[str, List[str]]]]:
        result = self.get_client().get_user(username)
        if not result:
            raise ValueError(f"Could not find user {username}.")
        if len(result) > 1:
            raise ValueError(f"Found multiple people.. {[person[0] for person in result]}.")
        person_ldap_details = result[0]
        dn, attributes = person_ldap_details
        return dn, attributes

    def _get_extra_attributes(
        self,
        username: str,  # noqa: ARG002
        attributes: Mapping[str, Union[str, List[str]]],
    ) -> Dict[str, Dict[str, str]]:
        """You can use any FontAwesome icons listed here; https://react-icons.github.io/react-icons/icons?name=fa"""
        return {
            "fullName": {
                "information": attributes["cn"][0],
                "icon": "FaUserCircle",
            },
            "location": {
                "information": attributes["l"][0],
                "icon": "FaMapMarkerAlt",
            },
        }

    def sync_person(self, person: Person, session: SASession) -> Person:  # noqa: ARG002
        filter_string: Optional[str] = person.username or person.email
        if filter_string is None:
            error_msg = f"It's not allowed to have both {person.username=} and {person.email=} be None."
            raise ValueError(error_msg)
        dn, attributes = self._extract_user_info(filter_string)
        person.username = dn.split("=")[1].split(",")[0]  # uid=abc,ou= -> extracts abc
        person.email = attributes["mail"][0]
        person.extra_attributes_json = json.dumps(self._get_extra_attributes(person.username, attributes))

        image_result = self._get_jpeg_photo_from_person(attributes)
        if image_result:
            image_in_bytes, width, height = image_result
            if person.image is None:
                person.image = PersonImage(image_in_bytes=image_in_bytes)
            else:
                person.image.image_in_bytes = image_in_bytes
            person.img_width = width
            person.img_height = height
        logger.debug(f"Updating references of {person}.")
        return person

    def _is_user_in_admin_group(self, username: str) -> bool:
        return any(self.get_client().is_user_in_group(username, group) for group in self.LDAP_ADMIN_GROUP_NAMES)

    async def admin_login_attempt(self, username: str, password: str) -> bool:  # noqa: ARG002
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result: bool = await loop.run_in_executor(pool, self._is_user_in_admin_group, username)
            return result


# Left this code here, so you can copy-paste this code to your extension and check whether your setup works.
# This requires you to set the `LDAP_FULL_QUANTIFIED_USERNAME` and `LDAP_PASSWORD` environment variables though.
if __name__ == "__main__":
    example_person = Person(username="some_username")
    plugin = LDAPPluginMixin()
    from sqlalchemy.orm import create_session

    with create_session() as session:
        plugin.sync_person(example_person, session=session)
        import pprint

        pprint.pprint(example_person)  # noqa: T203
