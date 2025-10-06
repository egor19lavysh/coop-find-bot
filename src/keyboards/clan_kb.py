from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST
from models.clan import Clan


async def get_update_clan_kb(clan_id: int) -> InlineKeyboardBuilder:
    buttons = [
        InlineKeyboardButton(text="Показать профиль клана", callback_data=f"read_clan_self_{clan_id}"),
        InlineKeyboardButton(text="Заполнить анкету клану заново 📝", callback_data=f"recreate_clan_{clan_id}"),
        InlineKeyboardButton(text="Удалить клан❌", callback_data=f"delete_clan_{clan_id}"),
        InlineKeyboardButton(text="Изменить фото 🖼️", callback_data=f"update_clan_photo_{clan_id}")
    ]

    builder = InlineKeyboardBuilder()

    for button in buttons:
        builder.add(button)

    builder.adjust(1)

    return builder.as_markup()

async def get_clan_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Создать новый клан", callback_data="create_clan")],
        [InlineKeyboardButton(text="Мои кланы", callback_data=f"get_all_user_clans")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_clans_kb(clans: list[Clan]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for clan in clans:
        builder.add(
            InlineKeyboardButton(
                text=clan.name,
                callback_data=f"detail_clan_{clan.id}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data="clan"
        )
    )

    builder.adjust(1)

    return builder.as_markup()


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