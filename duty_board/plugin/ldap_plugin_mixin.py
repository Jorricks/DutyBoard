import json
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Any, ClassVar, Dict, Final, List, Literal, Mapping, Optional, Tuple, Union

from ldap3 import Connection, Server, SUBTREE
from ldap3.core import exceptions
from sqlalchemy.orm import Session as SASession

from duty_board.models.person import Person

logger = logging.getLogger(__name__)


def ldap_rebind(func):
    @wraps(func)
    def wrapper(ldap_instance: "LdapBaseClient", *args: Any, **kwargs: Any) -> Any:
        try:
            return func(ldap_instance, *args, **kwargs)
        except (exceptions.LDAPSocketOpenError, exceptions.LDAPSessionTerminatedByServerError):
            ldap_instance.connection.unbind()
            ldap_instance.connection.bind()
            return func(ldap_instance, *args, **kwargs)

    return wrapper


class LdapBaseClient:
    def __init__(
        self,
        url: str,
        domain_components: str,
        user_organizational_unit: str,
        full_quantified_username: str,
        password: str,
        auto_referrals: bool = False,
    ):
        self.url: Final[str] = url
        self.domain_components: Final[str] = domain_components
        self.user_organizational_unit: Final[str] = user_organizational_unit
        self.connection = self._create_connection(full_quantified_username, password, auto_referrals=auto_referrals)

    def get_user(self, user_search_term: str) -> Optional[List[Tuple[str, Mapping[str, List[str]]]]]:
        if "." and "@" in user_search_term:
            search_filter = f"(mail={user_search_term})"
        elif "@" in user_search_term:
            search_filter = f"(uid={user_search_term.split('@')[0]})"
        else:
            search_filter = f"(uid={user_search_term})"

        if self.user_organizational_unit:
            search_base = f"{self.user_organizational_unit},{self.domain_components}"
        else:
            search_base = self.domain_components
        return self._search(search_filter, search_base, "*")

    def _create_connection(self, bind_dn: str, password: str, auto_referrals: bool) -> Connection:
        try:
            server = Server(host=self.url)
            connection = Connection(
                server=server,
                user=bind_dn,
                password=password,
                auto_referrals=auto_referrals,
                raise_exceptions=True,
            )
            connection.bind()
        except exceptions.LDAPInvalidServerError as exc:
            raise exceptions.LDAPException(f"Unable to connect to ldap url: {self.url}.") from exc
        except exceptions.LDAPInvalidCredentialsResult as exc:
            raise exceptions.LDAPException(f"Incorrect credentials for ldap url: {self.url}.") from exc
        except exceptions.LDAPInvalidDNSyntaxResult as exc:
            raise exceptions.LDAPException(f"Invalid bind user: {bind_dn}.") from exc
        if not connection.bound:
            raise exceptions.LDAPException(f"LDAP not bound for url {self.url}")
        return connection

    @ldap_rebind
    def _search(
        self,
        filter_str: str,
        base: str,
        attr_list: Optional[List[str]] = None,
        scope: Literal["BASE", "LEVEL", "SUBTREE"] = SUBTREE,
    ) -> Optional[List[Tuple[str, Mapping[str, List[str]]]]]:
        search_success = self.connection.search(base, filter_str, search_scope=scope, attributes=attr_list)
        if not search_success or not self.connection.response or not self.connection.response[0]:
            return None
        return [(item["dn"], item["attributes"]) for item in self.connection.response]


class LDAPPluginMixin:
    # LDAP settings
    LDAP_URL: ClassVar[str] = "ldaps://some.ldap.server.com:636"
    LDAP_DOMAIN_COMPONENTS: ClassVar[str] = "dc=your,dc=com"
    LDAP_USER_ORGANIZATIONAL_UNIT: ClassVar[str] = "ou=People"
    # This should be the same as you mention in your Plugin.
    LOCATION_TO_STORE_PHOTOS: ClassVar[Path] = Path("/tmp/photos")

    def __init__(self, *args, **kwargs):
        self.client = LdapBaseClient(
            url=self.LDAP_URL,
            domain_components=self.LDAP_DOMAIN_COMPONENTS,
            user_organizational_unit=self.LDAP_USER_ORGANIZATIONAL_UNIT,
            full_quantified_username=os.environ["LDAP_FULL_QUANTIFIED_USERNAME"],
            password=os.environ["LDAP_PASSWORD"],
            auto_referrals=False,
        )
        super(LDAPPluginMixin, self).__init__(*args, **kwargs)

    def _write_image_attribute_to_file(
        self, person: Person, person_attributes: Mapping[str, Union[str, List[str]]]
    ) -> Optional[str]:
        if "jpegPhoto" not in person_attributes:
            return None

        filepath = self.LOCATION_TO_STORE_PHOTOS / f"{person.uid}.jpg"
        with open(filepath, "wb") as file:
            img_as_b64: bytes = person_attributes["jpegPhoto"][0]  # type: ignore
            file.write(img_as_b64)
        return filepath.name

    def _extract_user_info(self, username: str) -> Tuple[str, Mapping[str, Union[str, List[str]]]]:
        result = self.client.get_user(username)
        if not result:
            raise ValueError(f"Could not find user {username}.")
        if len(result) > 1:
            raise ValueError(f"Found multiple people.. {[person[0] for person in result]}.")
        person_ldap_details = result[0]
        dn, attributes = person_ldap_details
        return dn, attributes

    def _get_extra_attributes(
        self, username: str, attributes: Mapping[str, Union[str, List[str]]]
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

    def sync_person(self, person: Person, session: SASession) -> Person:
        dn, attributes = self._extract_user_info(person.username or person.email)
        person.username = dn.split("=")[1].split(",")[0]  # uid=abc,ou= -> extracts abc
        person.email = attributes["mail"][0]
        person.img_filename = self._write_image_attribute_to_file(person, attributes)
        person.extra_attributes_json = json.dumps(self._get_extra_attributes(person.username, attributes))
        logger.debug(f"Updating references of {person}.")
        return person


# Left this code here, so you can copy-paste this code to your extension and check whether your setup works.
# This requires you to set the `LDAP_FULL_QUANTIFIED_USERNAME` and `LDAP_PASSWORD` environment variables though.
if __name__ == "__main__":
    example_person = Person(ldap="some_username")
    plugin = LDAPPluginMixin()
    from sqlalchemy.orm import create_session

    with create_session() as session:
        plugin.sync_person(example_person, session=session)
        import pprint

        pprint.pprint(example_person)
