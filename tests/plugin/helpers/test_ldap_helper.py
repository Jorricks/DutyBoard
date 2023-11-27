import pytest

from duty_board.plugin.helpers.ldap_helper import LDAPBaseClient


@pytest.fixture()
def ldap_base_client() -> LDAPBaseClient:
    return LDAPBaseClient(
        url="ldap://127.0.0.1:1389",
        base_dn="dc=DutyBoard,dc=com",
        user_organizational_unit="People",
        group_organizational_unit="Groups",
        account_attribute="uid",
        group_attribute="cn",
        ldap_group_membership_relation=("groupOfUniqueNames", "uniquemember"),
        full_quantified_username="cn=admin,dc=DutyBoard,dc=com",
        password="adminpassword",  # noqa: S106
        auto_referrals=False,
    )


def test_get_user(ldap_base_client: LDAPBaseClient) -> None:
    result = ldap_base_client.get_user("jan")
    assert result is not None
    assert len(result) == 1
    jan = result[0]
    assert len(jan) == 2
    assert jan[0] == "uid=jan,ou=People,dc=DutyBoard,dc=com"
    jan_attributes = jan[1]
    expected_items = [
        "cn",
        "gidNumber",
        "homeDirectory",
        "jpegPhoto",
        "l",
        "mail",
        "objectClass",
        "sn",
        "uid",
        "uidNumber",
        "userPassword",
    ]
    assert sorted(jan_attributes.keys()) == expected_items
    assert jan_attributes["cn"] == ["Jan Schoenmakers"]
    assert jan_attributes["gidNumber"] == 1000  # type: ignore[comparison-overlap]
    assert jan_attributes["homeDirectory"] == "/home/jan"  # type: ignore[comparison-overlap]
    assert jan_attributes["l"] == ["Amsterdam, NL"]
    assert jan_attributes["mail"] == ["jan@schoenmaker.nl"]
    assert jan_attributes["objectClass"] == ["inetOrgPerson", "posixAccount", "shadowAccount"]
    assert jan_attributes["sn"] == ["Bar1"]
    assert jan_attributes["uid"] == ["user01", "jan"]
    assert jan_attributes["uidNumber"] == 1000  # type: ignore[comparison-overlap]
    assert jan_attributes["userPassword"] == [b"JansWachtwoord"]  # type: ignore[comparison-overlap]

    result = ldap_base_client.get_user("non-existing-jan")
    assert result is None


def test_is_existing_user(ldap_base_client: LDAPBaseClient) -> None:
    assert ldap_base_client.is_existing_user("jan") is True
    assert ldap_base_client.is_existing_user("henk") is True
    assert ldap_base_client.is_existing_user("non-existing-jan") is False


def test_is_existing_group(ldap_base_client: LDAPBaseClient) -> None:
    # GroupOfUniqueNames
    assert ldap_base_client.is_existing_group("uniqueReaders") is True
    assert ldap_base_client.is_existing_group("admin-unique-interface") is True
    # Because this is groupOfNames!=groupOfUniqueNames.
    assert ldap_base_client.is_existing_group("readers") is False
    assert ldap_base_client.is_existing_group("admin-interface") is False
    # Random non existing group
    assert ldap_base_client.is_existing_group("non-existing-group") is False


def test_get_group_users_recursively(ldap_base_client: LDAPBaseClient) -> None:
    assert ldap_base_client.get_group_users_recursively(group_name="admin-unique-interface") == ["jan"]
    assert ldap_base_client.get_group_users_recursively(group_name="recursive-group") == ["henk", "jan"]


def test_is_user_in_group(ldap_base_client: LDAPBaseClient) -> None:
    assert ldap_base_client.is_user_in_group(username="jan", group_name="admin-unique-interface") is True
    assert ldap_base_client.is_user_in_group(username="henk", group_name="admin-unique-interface") is False

    assert ldap_base_client.is_user_in_group(username="jan", group_name="recursive-group") is True
    assert ldap_base_client.is_user_in_group(username="henk", group_name="recursive-group") is True

    assert ldap_base_client.is_user_in_group(username="jan-not-exist", group_name="admin-unique-interface") is False
    assert ldap_base_client.is_user_in_group(username="jan", group_name="non-existing_group") is False


def test_ldap_rebind(ldap_base_client: LDAPBaseClient) -> None:
    assert ldap_base_client.is_existing_group("uniqueReaders") is True
    ldap_base_client.connection.unbind()
    assert ldap_base_client.is_existing_group("uniqueReaders") is True
