from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot.handlers import captcha


@pytest.mark.asyncio
async def test_captcha_pass_deletes_existing_user_challenge(monkeypatch: pytest.MonkeyPatch) -> None:
    message = SimpleNamespace(delete=AsyncMock(), answer=AsyncMock())
    callback_query = SimpleNamespace(from_user=SimpleNamespace(id=42), message=message)
    session = object()

    monkeypatch.setattr(captcha, "_", lambda key: key)
    monkeypatch.setattr(captcha, "user_exists", AsyncMock(return_value=True))
    send_main_menu = AsyncMock()
    monkeypatch.setattr(captcha, "send_main_menu", send_main_menu)

    await captcha.captcha_pass_handler(callback_query, bot=AsyncMock(), session=session)

    message.delete.assert_awaited_once()
    send_main_menu.assert_awaited_once_with(message, session=session, user_id=42)
