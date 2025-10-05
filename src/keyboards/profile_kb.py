from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST, FIELDS_LIST

TEXT_BACK = "Назад"

async def get_skip_keyboard(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text="Пропустить")]]
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def get_gender_keyboard(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Мужской")],
        [KeyboardButton(text="Женский")],
        [KeyboardButton(text="Пропустить")]
    ]
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
        
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def get_game_kb(with_back: bool = True, n: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(
            InlineKeyboardButton(text=game,
                                 callback_data=f"save_profile_game_{game}")
        )
    
    if with_back:
        builder.add(InlineKeyboardButton(text="Назад", callback_data="back_from_games"))
    
    builder.adjust(n)
    keyboard = builder.as_markup()
    return keyboard

async def get_photo_kb(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Фото с профиля")],
        [KeyboardButton(text="Пропустить")]
    ]
    
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

async def get_confirmation_kb(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")]
    ]
    
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

async def get_tag_kb(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Отправить данные")],
        [KeyboardButton(text="Пропустить")]
    ]
    
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

async def get_commit_profile_kb(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Верно ✅")],
        [KeyboardButton(text="Неверно ❌")]
    ]
    
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

async def get_status_kb(with_back: bool = True) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Подтвердить ✅", callback_data="is_active_true")
    )
    builder.add(
        InlineKeyboardButton(text="Отклонить ❌", callback_data="is_active_false")
    )
    
    if with_back:
        builder.add(
            InlineKeyboardButton(text="Назад", callback_data="back_from_status")
        )
    
    builder.adjust(1)
    return builder

# Остальные клавиатуры остаются без изменений
async def get_game_inline_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура для выбора игр"""
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(InlineKeyboardButton(
            text=game,
            callback_data=f"get_profiles_by_{game}"
        ))
    
    builder.adjust(2)
    return builder.as_markup()

async def get_update_profile_kb(user_id: int) -> InlineKeyboardBuilder:
    buttons = [
        InlineKeyboardButton(text="Показать профиль", callback_data=f"read_profile_self_{user_id}"),
        InlineKeyboardButton(text="Заполнить анкету заново 📝", callback_data="edit_profile"),
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

async def get_edit_fields_kb():
    keyboard = [
        [
            InlineKeyboardButton(text="Никнейм", callback_data="edit_nickname"),
        ],
        [
            InlineKeyboardButton(text="Тег Telegram", callback_data="edit_telegram_tag"),
        ],
        [
            InlineKeyboardButton(text="Пол", callback_data="edit_gender"),
        ],
        [  
            InlineKeyboardButton(text="Игры", callback_data="edit_games"),
        ],
        [
            InlineKeyboardButton(text="О себе", callback_data="edit_about"),
        ],
        [
            InlineKeyboardButton(text="Цель", callback_data="edit_goal"),
        ],
        [
           InlineKeyboardButton(text="Фото", callback_data="edit_photo")
        ],
        [
            InlineKeyboardButton(text="Отмена", callback_data="edit_cancel"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)