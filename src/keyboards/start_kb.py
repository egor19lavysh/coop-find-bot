from aiogram import Bot, types, Dispatcher, F, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_keyboard(user_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Перейти",
            url="https://t.me/ggstore_hub"
        )
    )

    builder.add(
        InlineKeyboardButton(
            text="Проверить✅",
            callback_data=f"check_sub_{user_id}"
        )
    )

    builder.adjust(1)

    return builder
