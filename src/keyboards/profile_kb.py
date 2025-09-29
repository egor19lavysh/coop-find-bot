from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

async def get_status_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Подтвердить ✅")],
        [KeyboardButton(text="Отклонить ❌")]
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    return keyboard

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