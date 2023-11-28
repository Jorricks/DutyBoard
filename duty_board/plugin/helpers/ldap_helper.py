import logging
import sys
from functools import wraps
from typing import (
    Callable,
    Final,
    List,
    Literal,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from ldap3 import SUBTREE, Connection, Server
from ldap3.core import exceptions
from ldap3.core.exceptions import LDAPNoSuchObjectResult
from pydantic import BaseModel

if sys.version_info[:2] >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


logger = logging.getLogger(__name__)
P = ParamSpec("P")
R = TypeVar("R")


class LdapGroupDoesNotExistError(Exception):
    pass


def ldap_rebind(func: Callable[P, R]):  # type: ignore
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ldap_instance = args[0]
        if not isinstance(ldap_instance, LDAPBaseClient):
            raise TypeError(f"Unexpected first argument; {args[0]}.")
        try:
            return func(*args, **kwargs)
        except (exceptions.LDAPSocketOpenError, exceptions.LDAPSessionTerminatedByServerError):
            ldap_instance.connection.unbind()
            ldap_instance.connection.bind()
            return func(*args, **kwargs)

    return wrapper


class LDAPPersonSearch(BaseModel):
    base_dn: str
    account_attribute: str
    organization_unit: Optional[str] = None
    name: str

    @property
    def search_filter(self) -> str:
        if "." and "@" in self.name:
            return f"(mail={self.name})"
        if "@" in self.name:
            return f"({self.account_attribute}={self.name.split('@')[0]})"
        return f"({self.account_attribute}={self.name})"

    @property
    def person_dn(self) -> str:
        if self.organization_unit:
            return f"ou={self.organization_unit},{self.base_dn}"
        return self.base_dn


class LDAPGroupSearch(BaseModel):
    base_dn: str
    group_attribute: str
    organization_unit: Optional[str] = None
    ldap_group_membership_relation: Tuple[str, str]
    name: str

    @property
    def search_filter(self) -> str:
        return f"(&(ObjectClass={self.ldap_group_membership_relation[0]})({self.group_attribute}={self.name}))"

    @property
    def group_dn(self) -> str:
        if self.organization_unit:
            return f"ou={self.organization_unit},{self.base_dn}"
        return self.base_dn

    @property
    def dn(self) -> str:
        return f"{self.group_attribute}={self.name},{self.group_dn}"


class LDAPBaseClient:
    def __init__(  # noqa: PLR0913
        self,
        url: str,  # e.g. ldaps://some.ldap.server.com:636
        base_dn: str,  # e.g. dc=example,dc=com
        user_organizational_unit: Optional[str],  # e.g. People
        group_organizational_unit: Optional[str],  # e.g. Group
        account_attribute: str,  # e.g. uid
        group_attribute: str,  # e.g. cn
        ldap_group_membership_relation: Tuple[str, str],  # e.g. ("groupOfUniqueNames", "uniquemember")
        full_quantified_username: str,  # e.g. uid=jorrick,ou=People,dc=example,dc=com
        password: str,
        auto_referrals: bool = False,
    ):
        self.url: Final[str] = url
        self.base_dn: Final[str] = base_dn
        self.user_organizational_unit: Final[Optional[str]] = user_organizational_unit
        self.group_organizational_unit: Final[Optional[str]] = group_organizational_unit
        self.account_attribute: Final[str] = account_attribute
        self.group_attribute: Final[str] = group_attribute
        self.ldap_group_membership_relation: Final[Tuple[str, str]] = ldap_group_membership_relation
        self.connection: Connection = self._create_connection(
            full_quantified_username,
            password,
            auto_referrals=auto_referrals,
        )

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
        try:
            search_success = self.connection.search(base, filter_str, search_scope=scope, attributes=attr_list)
        except LDAPNoSuchObjectResult:
            return None
        if not search_success or not self.connection.response or not self.connection.response[0]:
            return None
        return [(item["dn"], item["attributes"]) for item in self.connection.response]

    def _extract_name(self, item: Optional[List[Tuple[str, Mapping[str, List[str]]]]], i: int) -> Optional[str]:
        try:
            return item[i][1][self.group_attribute][0]  # type: ignore[index]
        except (IndexError, TypeError):
            return None

    def __get_group_search(self, group_name: str) -> LDAPGroupSearch:
        return LDAPGroupSearch(
            base_dn=self.base_dn,
            group_attribute=self.group_attribute,
            organization_unit=self.group_organizational_unit,
            ldap_group_membership_relation=self.ldap_group_membership_relation,
            name=group_name,
        )

    def _get_group_cn(self, group_name: str) -> Optional[str]:
        group_search = self.__get_group_search(group_name=group_name)
        search_result = self._search(
            filter_str=group_search.search_filter,
            base=group_search.group_dn,
            attr_list=[group_search.group_attribute],
        )
        return self._extract_name(search_result, 0)

    def _get_group_members(self, group_name: str) -> Tuple[List[str], List[str]]:
        group_search = self.__get_group_search(group_name=group_name)
        search_result = self._search(
            filter_str=f"(&(ObjectClass={self.ldap_group_membership_relation[0]}))",  # e.g. "groupOfUniqueNames"
            base=group_search.dn,
            attr_list=[self.ldap_group_membership_relation[1]],
        )
        if (not search_result) and (not self.is_existing_group(group_name)):
            raise LdapGroupDoesNotExistError(f"The group {group_name} does not exist as {group_search.dn} on LDAP.")

        dn_list: List[str] = search_result[0][1][self.ldap_group_membership_relation[1]]  # e.g. "uniquemember"
        user_list: List[str] = []
        group_list: List[str] = []
        for dn in dn_list:
            if self.user_organizational_unit is not None and f"ou={self.user_organizational_unit}," in dn:
                user_list.append(dn)
            elif self.group_organizational_unit is not None and f"ou={self.group_organizational_unit}," in dn:
                group_list.append(dn)
            elif self.account_attribute != self.group_attribute:
                if dn.startswith(self.group_attribute):
                    group_list.append(dn)
                elif dn.startswith(self.account_attribute):
                    user_list.append(dn)
                else:
                    logger.warning(f"Ignoring {dn=} as it seems to be neither a group nor a user.")
            else:
                logger.warning(f"Unable to distinguish users from groups. Assuming {dn=} is a user.")
                user_list.append(dn)
        return user_list, group_list

    def get_user(
        self,
        username: str,
        attributes: Optional[List[str]] = None,
    ) -> Optional[List[Tuple[str, Mapping[str, List[str]]]]]:
        person_search: LDAPPersonSearch = LDAPPersonSearch(
            base_dn=self.base_dn,
            account_attribute=self.account_attribute,
            organization_unit=self.user_organizational_unit,
            name=username,
        )
        return self._search(  # type: ignore[no-any-return]
            person_search.search_filter,
            person_search.person_dn,
            attributes or ["*"],
        )

    def is_existing_user(self, username: str) -> bool:
        return self.get_user(username) is not None

    def is_existing_group(self, group_name: str) -> bool:
        group_cn = self._get_group_cn(group_name)
        return group_cn is not None and len(group_cn) > 0

    def get_group_users_recursively(self, group_name: str, groups_seen: Optional[Set[str]] = None) -> List[str]:
        all_users: Set[str] = set()
        groups_seen = groups_seen or set()
        users, groups = self._get_group_members(group_name)
        all_users.update([user.split(",")[0].split("=")[1] for user in users])  # uid=jorrick,dc... -> jorrick
        for group in groups:
            group_name = group.split(",")[0].split("=")[1]
            if group_name not in groups_seen:
                all_users.update(self.get_group_users_recursively(group_name, {*groups_seen, group_name}))
        return sorted(all_users)

    def is_user_in_group(self, username: str, group_name: str) -> bool:
        return (
            self.is_existing_user(username)
            and self.is_existing_group(group_name)
            and username in self.get_group_users_recursively(group_name)
        )
