from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
    [InlineKeyboardButton(text="Начать поиск 🔍", callback_data="start_search")],
    [InlineKeyboardButton(text="📝Моя анкета📝", callback_data="profile"),
    InlineKeyboardButton(text="⚔️Мои кланы⚔️", callback_data="clan")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
