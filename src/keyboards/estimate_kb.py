from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import CONNECT_LIST


async def get_connect_kb() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=btn_text)] for btn_text in CONNECT_LIST]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

async def get_scale_kb(field: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="1️⃣", callback_data=f"estimate_{field}_1"),
        InlineKeyboardButton(text="2️⃣", callback_data=f"estimate_{field}_2"),
        InlineKeyboardButton(text="3️⃣", callback_data=f"estimate_{field}_3"),
        InlineKeyboardButton(text="4️⃣", callback_data=f"estimate_{field}_4"),
        InlineKeyboardButton(text="5️⃣", callback_data=f"estimate_{field}_5"),
    ]

    for button in buttons:
        builder.add(button)

    builder.adjust(5)

    return builder.as_markup()


async def get_search_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Начать поиск 🔍", callback_data="start_search"))
    builder.adjust(1)
    return builder.as_markup()

async def get_success_kb() -> ReplyKeyboardMarkup:
    button = InlineKeyboardButton(text="Да, получилось✅", callback_data="estimate_callback")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])