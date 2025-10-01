from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST


async def get_skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True  # рекомендуется добавлять для лучшего отображения
    )

async def get_gender_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Мужской")],
        [KeyboardButton(text="Женский")],
        [KeyboardButton(text="Пропустить")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

async def get_game_kb() -> ReplyKeyboardMarkup:
    buttons = []
    for game in GAME_LIST:
        buttons.append([KeyboardButton(text=game)])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

async def get_status_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Подтвердить ✅", callback_data="is_active_true")
    )
    builder.add(
        InlineKeyboardButton(text="Отклонить ❌", callback_data="is_active_false")
    )
    builder.adjust(1)
    return builder

async def get_commit_profile_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Верно ✅")],
        [KeyboardButton(text="Неверно ❌")]
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    return keyboard


async def get_update_profile_kb(user_id: int) -> InlineKeyboardBuilder:
    buttons = [
        InlineKeyboardButton(text="Просмотреть анкету 👤", callback_data=f"read_profile_self_{user_id}"),
        InlineKeyboardButton(text="Заполнить анкету заново 📝", callback_data="recreate_profile"),
        InlineKeyboardButton(text="Удалить анкету❌", callback_data="delete_profile"),
        InlineKeyboardButton(text="Изменить фото 🖼️", callback_data="update_photo"),
        InlineKeyboardButton(text="Снять анкету ⏸️", callback_data="deactivate_profile"),
        InlineKeyboardButton(text="Разместить анкету 📢", callback_data="activate_profile")
    ]

    builder = InlineKeyboardBuilder()

    for button in buttons:
        builder.add(button)

    builder.adjust(1)

    return builder

async def get_interaction_kb(user_id: int, game: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text="Написать сообщение",
            callback_data=f"send_message_to_user_{user_id}"
        )],
        [InlineKeyboardButton(
            text="Пригласить в игру",
            callback_data=f"invite_user_{game}_{user_id}"
        )],
        [InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_profiles"
        )]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    return keyboard