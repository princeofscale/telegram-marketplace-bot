import pytest

from bot.modules.admins.policy import is_default_admin_user, parse_admin_user_ids


def test_parse_admin_user_ids_accepts_comma_and_semicolon_lists() -> None:
    assert parse_admin_user_ids("1314697368, 42; 7") == frozenset({1314697368, 42, 7})


def test_parse_admin_user_ids_ignores_empty_values() -> None:
    assert parse_admin_user_ids("  , ; ") == frozenset()
    assert parse_admin_user_ids(None) == frozenset()


def test_parse_admin_user_ids_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="invalid literal"):
        parse_admin_user_ids("1314697368,not-a-user-id")


def test_is_default_admin_user_checks_membership() -> None:
    admin_user_ids = frozenset({1314697368})

    assert is_default_admin_user(1314697368, admin_user_ids)
    assert not is_default_admin_user(42, admin_user_ids)
