from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot.utils.messages import get_section_image_path, replace_message_text


@pytest.mark.asyncio
async def test_replace_message_text_edits_text_messages() -> None:
    message = SimpleNamespace(text="old text", edit_text=AsyncMock(), delete=AsyncMock(), answer=AsyncMock())

    await replace_message_text(message, "new text", reply_markup=None)

    message.edit_text.assert_awaited_once_with("new text", reply_markup=None)
    message.delete.assert_not_awaited()
    message.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_replace_message_text_replaces_non_text_messages() -> None:
    message = SimpleNamespace(text=None, message_id=1, edit_text=AsyncMock(), delete=AsyncMock(), answer=AsyncMock())

    await replace_message_text(message, "new text", reply_markup=None)

    message.edit_text.assert_not_awaited()
    message.delete.assert_awaited_once()
    message.answer.assert_awaited_once_with("new text", reply_markup=None)


def test_section_image_paths_cover_requested_sections() -> None:
    assert get_section_image_path("help").name == "help.png"
    assert get_section_image_path("profile").name == "profile.png"
    assert get_section_image_path("unknown").name == "other.png"
