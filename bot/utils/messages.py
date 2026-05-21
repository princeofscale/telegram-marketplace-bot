from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramAPIError
from aiogram.types import FSInputFile
from loguru import logger

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup, Message

TELEGRAM_PHOTO_CAPTION_LIMIT = 1024
IMAGES_DIR = Path(__file__).resolve().parents[2] / "images"

SECTION_IMAGES = {
    "catalog": ("catalog.png", "other.png"),
    "help": ("help.png", "other.png"),
    "info": ("info.png", "other.png"),
    "menu": ("menu.jpg", "menu.png", "other.png"),
    "other": ("other.png",),
    "profile": ("profile.png", "other.png"),
    "settings": ("settings.png", "other.png"),
}


def get_section_image_path(section: str) -> Path | None:
    for filename in SECTION_IMAGES.get(section, SECTION_IMAGES["other"]):
        image_path = IMAGES_DIR / filename
        if image_path.exists():
            return image_path
    return None


async def replace_message_text(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if message.text:
        await message.edit_text(text, reply_markup=reply_markup)
        return

    try:
        await message.delete()
    except TelegramAPIError as exc:
        logger.warning(f"failed to delete non-text message | message_id: {message.message_id} | error: {exc}")

    await message.answer(text, reply_markup=reply_markup)


async def send_section_message(
    message: Message,
    text: str,
    *,
    section: str = "other",
    reply_markup: InlineKeyboardMarkup | None = None,
    edit: bool = False,
) -> None:
    image_path = get_section_image_path(section)
    if image_path is None or len(text) > TELEGRAM_PHOTO_CAPTION_LIMIT:
        if edit:
            await replace_message_text(message, text, reply_markup=reply_markup)
            return
        await message.answer(text, reply_markup=reply_markup)
        return

    if edit:
        try:
            await message.delete()
        except TelegramAPIError as exc:
            logger.warning(
                f"failed to delete message before section photo | message_id: {message.message_id} | error: {exc}",
            )

    await message.answer_photo(FSInputFile(image_path), caption=text, reply_markup=reply_markup)
