from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.constants import GAME_LIST, FIELDS_LIST, GOALS_LIST, CONVENIENT_TIME
from utils.ranks import *
from models.profile import Game

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

async def get_back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXT_BACK)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def get_gender_keyboard(with_back: bool = True) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Мужской", callback_data="gender_Мужской")],
        [InlineKeyboardButton(text="Женский", callback_data="gender_Женский")],
        [InlineKeyboardButton(text="Пропустить", callback_data="gender_skip")]
    ]
    if with_back:
        buttons.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"gender_back")])
        
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    return keyboard

async def get_game_kb(with_back: bool = True, n: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(
            InlineKeyboardButton(text=GAME_LIST[game],
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

async def get_confirmation_kb(with_back: bool = True) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data="confirm_Да")],
        [InlineKeyboardButton(text="Нет", callback_data="confirm_Нет")]
    ]
    
    if with_back:
        buttons.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"confirm_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_tag_kb(with_back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Отправить данные")],
        [KeyboardButton(text="Пропустить")]
    ]
    
    if with_back:
        buttons.append([KeyboardButton(text=TEXT_BACK)])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

async def get_commit_profile_kb(with_back: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="Верно ✅", callback_data="profile_correct")
    builder.button(text="Неверно ❌", callback_data="profile_incorrect")
    if with_back:
        builder.button(text=TEXT_BACK, callback_data="back_from_check")
    builder.adjust(2)
    return builder.as_markup()

async def get_status_kb(with_back: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="Разрешить ✅", callback_data="status_true")
    builder.button(text="Запретить ❌", callback_data="status_false")
    if with_back:
        builder.button(text=TEXT_BACK, callback_data="back_from_status")
    builder.adjust(2)
    return builder.as_markup()

# Остальные клавиатуры остаются без изменений
async def get_game_inline_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура для выбора игр"""
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(InlineKeyboardButton(
            text=GAME_LIST[game],
            callback_data=f"get_profiles_by_{game}"
        ))
    
    builder.adjust(2)
    return builder.as_markup()

async def get_profile_kb(user_id: int) -> InlineKeyboardBuilder:
    buttons = [
        InlineKeyboardButton(text="Создать анкету", callback_data="create_profile"),
        InlineKeyboardButton(text="Показать профиль", callback_data=f"read_profile_self_{user_id}"),
        InlineKeyboardButton(text="Изменить анкету📝", callback_data="edit_profile"),
        InlineKeyboardButton(text="Удалить анкету❌", callback_data="delete_profile"),
        InlineKeyboardButton(text="Снять анкету ⏸️", callback_data="deactivate_profile"),
        InlineKeyboardButton(text="Разместить анкету 📢", callback_data="activate_profile"),
        InlineKeyboardButton(text="Назад", callback_data="menu")
    ]

    builder = InlineKeyboardBuilder()

    for button in buttons:
        builder.add(button)

    builder.adjust(1)

    return builder

async def get_interaction_kb(user_id: int, game: str, need_filter: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text="Галерея",
            callback_data=f"show_gallery_{user_id}_{game}" if not need_filter else f"show_gallery_filter_{user_id}_{game}"
        )],
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
            callback_data="back_to_profiles" if not need_filter else "profile_by_filters"
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
            InlineKeyboardButton(text="Удобное время", callback_data="edit_time"),
        ],
        [
            InlineKeyboardButton(text="О себе", callback_data="edit_about"),
        ],
        [
            InlineKeyboardButton(text="Цели", callback_data="edit_goal"),
        ],
        [
           InlineKeyboardButton(text="Фото", callback_data="edit_photo")
        ],
        [
            InlineKeyboardButton(text="Отмена", callback_data="profile"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_back_to_check_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться к проверке", callback_data="back_to_profile_check")
    return builder.as_markup()

async def get_back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="profile")]])

async def get_back_to_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="menu")]])

async def get_back_to_main_menu_from_invite(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="menu")],
                                    [InlineKeyboardButton(
                                                    text="Ответить",
                                                    url=f"https://t.me/{username}"
                                                )]              
                                                  ])

async def get_goals_kb(with_back: bool = False) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=goal, callback_data=f"goal_{goal}")] for goal in GOALS_LIST]
    if with_back:
        buttons.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"goals_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



async def get_ranks_kb(game: str, with_back: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    if game in GAMES_RANKS:
        for rank in GAMES_RANKS[game]:
            keyboard.append([InlineKeyboardButton(text=rank, callback_data=f"rank_{rank}")])
    
    keyboard.append([InlineKeyboardButton(text="Пропустить", callback_data=f"rank_skip")])

    if with_back:
        keyboard.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"rank_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
        

async def get_warcraft_modes_kb(with_back: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    for mode in WARCRAFT_MODES:
        keyboard.append([InlineKeyboardButton(text=mode, callback_data=f"mode_{mode}")])
    
    keyboard.append([InlineKeyboardButton(text="Пропустить", callback_data="mode_skip")])

    if with_back:
        keyboard.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"mode_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# async def get_warcraft_ranks_kb(is_pve: bool = False) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     ranks = WARCRAFT_PvE if is_pve else WARCRAFT
    
#     # Create a mapping for callback data
#     for rank in ranks:
#         # Use index or a short identifier instead of the full name
#         rank_index = ranks.index(rank)
#         builder.add(
#             InlineKeyboardButton(text=rank, callback_data=f"add_warcraft_rank/{rank_index}/{is_pve}")
#         )

#     builder.adjust(3)

#     builder.add(
#         InlineKeyboardButton(text="Назад", callback_data="back_from_warcraft_ranks")
#     )

#     return builder.as_markup()

async def get_warcraft_ranks_kb(is_pve: bool = False, page=0, per_page=18):
    """Клавиатура для отображения списка кланов"""
    builder = InlineKeyboardBuilder()
    ranks = WARCRAFT_PvE if is_pve else WARCRAFT
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    ranks_page = ranks[start_idx:end_idx]
    
    for rank in ranks_page:
        rank_index = ranks.index(rank)
        builder.add(
            InlineKeyboardButton(text=rank, callback_data=f"add_warcraft_rank/{rank_index}/{is_pve}")
        )

    builder.adjust(2)
    
    navigation_buttons = []
    
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"ranks_page_nopve_{page - 1}" if not is_pve else f"ranks_page_pve_{page - 1}"
            )
        )

    total_pages = (len(ranks) - 1) // per_page + 1 if ranks else 1
    navigation_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )
    
    if end_idx < len(ranks):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"ranks_page_nopve_{page + 1}" if not is_pve else f"ranks_page_pve_{page + 1}"
            )
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_from_warcraft_ranks"
        )
    )

    return builder.as_markup()


async def get_time_kb(with_back: bool = False) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=time, callback_data=f"time_{time}")] for time in CONVENIENT_TIME]

    if with_back:
        kb.append([InlineKeyboardButton(text=TEXT_BACK, callback_data=f"time_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_edit_games_kb(games: list[Game], process: str = "", new_game: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for game in games:
        builder.add(InlineKeyboardButton(
            text=f"{game.name}",
            callback_data=f"update_game_{game.name}"
        ))
    
    if new_game:
        builder.add(
            InlineKeyboardButton(
                text="Добавить игру",
                callback_data="add_new_game"
            )
        )

    if process != "creating_profile":
        builder.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data="edit_profile"
            )
        )
    else:
        builder.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data="get_back_from_games_to_creating_profile"
            )
        )


    builder.adjust(1)

    return builder.as_markup()

async def get_read_game_kb(game: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Ранг", callback_data=f"edit_rank_{game}")
    )

    builder.add(
        InlineKeyboardButton(text="Галерея", callback_data=f"edit_gallery_{game}")
    )

    builder.add(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete_game_{game}")
    )

    builder.add(
        InlineKeyboardButton(text="Назад", callback_data=f"update_games")
    )

    builder.adjust(1)

    return builder.as_markup()

