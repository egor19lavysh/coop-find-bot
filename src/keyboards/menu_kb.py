from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST


async def get_menu_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Начать поиск 🔍", callback_data="start_search"))
    builder.add(InlineKeyboardButton(text="Моя анкета", callback_data="profile"))
    builder.add(InlineKeyboardButton(text="Мои кланы", callback_data="clan"))
    builder.adjust(1)
    return builder
