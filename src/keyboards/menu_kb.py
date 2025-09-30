from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST


async def get_menu_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Редактировать анкету ✏️", callback_data="update_profile"))
    builder.add(InlineKeyboardButton(text="Начать поиск 🔍", callback_data="start_search"))
    builder.adjust(1)
    return builder