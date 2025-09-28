from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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