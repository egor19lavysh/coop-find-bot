from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST


async def get_update_clan_kb(user_id: int) -> InlineKeyboardBuilder:
    buttons = [
        InlineKeyboardButton(text="Показать профиль клана", callback_data=f"read_clan_self_{user_id}"),
        InlineKeyboardButton(text="Заполнить анкету клану заново 📝", callback_data="recreate_clan"),
        InlineKeyboardButton(text="Удалить клан❌", callback_data="delete_clan"),
        InlineKeyboardButton(text="Изменить фото 🖼️", callback_data="update_clan_photo")
    ]

    builder = InlineKeyboardBuilder()

    for button in buttons:
        builder.add(button)

    builder.adjust(1)

    return builder


async def get_interaction_kb(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text="Вступить в клан",
            callback_data=f"join_clan_{user_id}"
        )],
        [InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_clans"
        )]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    return keyboard