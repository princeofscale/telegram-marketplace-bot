from bot.keyboards.default_commands import users_commands


def test_only_start_command_is_registered() -> None:
    assert users_commands == {
        "en": {"start": "menu"},
        "uk": {"start": "меню"},
        "ru": {"start": "меню"},
    }
