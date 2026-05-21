import pytest
from aiogram.enums import ButtonStyle

from bot.database.models import CatalogProductModel
from bot.keyboards.inline import catalog, contacts, menu, settings
from bot.modules.catalog.callbacks import (
    BUY_CALLBACK_PREFIX,
    CATALOG_CALLBACK,
    CONFIRM_BUY_CALLBACK_PREFIX,
    PRODUCT_CALLBACK_PREFIX,
)
from bot.modules.profile.callbacks import LANGUAGE_SETTINGS_CALLBACK, SETTINGS_CALLBACK


def test_catalog_button_uses_primary_style(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(menu, "_", lambda key: key)

    keyboard = menu.main_keyboard()
    catalog_button = keyboard.inline_keyboard[0][0]

    assert catalog_button.callback_data == CATALOG_CALLBACK
    assert catalog_button.style == ButtonStyle.PRIMARY


def test_support_keyboard_has_support_and_back_buttons(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(contacts, "_", lambda key: key)

    keyboard = contacts.support_keyboard()

    assert keyboard.inline_keyboard[0][0].url
    assert keyboard.inline_keyboard[1][0].callback_data == "menu"


def test_settings_keyboard_opens_language_submenu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "_", lambda key: key)

    keyboard = settings.settings_keyboard()

    assert keyboard.inline_keyboard[0][0].callback_data == LANGUAGE_SETTINGS_CALLBACK
    assert keyboard.inline_keyboard[1][0].callback_data == "menu"


def test_language_settings_keyboard_returns_to_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "_", lambda key: key)

    keyboard = settings.language_settings_keyboard(current_language="ru")

    assert keyboard.inline_keyboard[-1][0].callback_data == SETTINGS_CALLBACK


def test_product_keyboard_opens_purchase_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(catalog, "_", lambda key: key)
    product = CatalogProductModel(title="Stars", category="telegram", display_price=100)

    keyboard = catalog.product_keyboard(product)

    assert keyboard.inline_keyboard[0][0].callback_data.startswith(f"{CONFIRM_BUY_CALLBACK_PREFIX}:")


def test_purchase_confirmation_keyboard_has_confirm_and_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(catalog, "_", lambda key: key)
    product = CatalogProductModel(title="Stars", category="telegram", display_price=100)

    keyboard = catalog.purchase_confirmation_keyboard(product)

    assert keyboard.inline_keyboard[0][0].callback_data.startswith(f"{BUY_CALLBACK_PREFIX}:")
    assert keyboard.inline_keyboard[1][0].callback_data.startswith(f"{PRODUCT_CALLBACK_PREFIX}:")
