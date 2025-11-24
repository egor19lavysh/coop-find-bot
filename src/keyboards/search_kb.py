from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile
from utils.constants import *
from utils.constants import GAME_LIST, FIELDS_LIST, GOALS_LIST, CONVENIENT_TIME
from utils.ranks import *


async def get_profiles_kb(profiles: list[Profile],  game: str, page: int = 0, per_page: int = 18, need_filter: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_profiles = profiles[start_idx:end_idx]
    
    for profile in current_profiles:
        if profile.polite is not None and profile.team_game is not None and profile.skill is not None:
            sa = (profile.polite + profile.team_game + profile.skill) / 3
            rating = round(sa, 1)
        else:
            rating = None
        
        rating_text = f" {rating}⭐" if rating is not None else ""
        
        builder.add(
            InlineKeyboardButton(
                text=f"{profile.nickname}, {game}{rating_text}".strip(),
                callback_data=f"read_profile_other_{profile.user_id}" if not need_filter else f"read_profile_other_filter_{profile.user_id}"
            )
        )
    
    profiles_count = len(current_profiles)
    sizes = []
    if profiles_count < per_page:
        for _ in range(profiles_count // 2):
            sizes.append(2)

    if profiles_count % 2 != 0:
        sizes.append(profiles_count % 2)
    
    builder.adjust(*sizes)


    
    navigation_buttons = []
    

    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"profiles_page_{page - 1}"
            )
        )
    
    total_pages = (len(profiles) - 1) // per_page + 1 if profiles else 1
    navigation_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )
    
    if end_idx < len(profiles):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"profiles_page_{page + 1}"
            )
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=f"search_type_profiles"
        )
    )
    
    return builder.as_markup()


async def get_search_type_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text="Анкеты игроков", 
            callback_data="search_type_profiles"
        )],
        [InlineKeyboardButton(
            text="Кланы", 
            callback_data="search_type_clans"
        )],
        [
            InlineKeyboardButton(
            text="Назад", 
            callback_data="menu"
        )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_clans_kb(clans, page=0, per_page=18):
    """Клавиатура для отображения списка кланов"""
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    clans_page = clans[start_idx:end_idx]
    
    for clan in clans_page:
        builder.add(InlineKeyboardButton(
            text=f"{clan.name}",
            callback_data=f"view_clan_{clan.id}" 
        ))

    builder.adjust(2)
    
    navigation_buttons = []
    
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"clans_page_{page - 1}"
            )
        )

    total_pages = (len(clans) - 1) // per_page + 1 if clans else 1
    navigation_buttons.append(
        InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        )
    )
    
    if end_idx < len(clans):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"clans_page_{page + 1}"
            )
        )
    
    if navigation_buttons:
        builder.row(*navigation_buttons)
    
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=f"search_type_clans"
        )
    )

    return builder.as_markup()

async def get_clan_detail_kb(clan_id: int, game: str) -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра клана"""
    buttons = [
        [InlineKeyboardButton(
            text="Отправить заявку",
            callback_data=f"join_clan_{clan_id}"
        )],
        [InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_clans"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_back_kb(search_type: str = "profiles") -> InlineKeyboardMarkup:
    callback_data = "back_to_profiles" if search_type == "profiles" else "back_to_clans"
    
    buttons = [
        [InlineKeyboardButton(
            text=f"Назад",
            callback_data=callback_data
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



async def get_profile_action_kb(user_id: int, game: str) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для профиля пользователя"""
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
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_game_inline_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура для выбора игр"""
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(InlineKeyboardButton(
            text=game,
            callback_data=f"get_profiles_by_{game}"
        ))
    
    builder.adjust(2)

    builder.row(InlineKeyboardButton(text="Назад", callback_data="start_search"))
    return builder.as_markup()

async def get_back_to_games_kb(search_type: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"search_type_{search_type}")]]
    )

async def get_invite_profile_kb(user_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Его профиль", callback_data=f"read_profile_invite_{user_id}")]]
    )


async def get_to_dialog_with_user_kb(username: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Ответить",
            url=f"https://t.me/{username}"
        )]
    ])
    return keyboard

async def get_search_profiles_types():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поиск", callback_data="filter_search")],
        [InlineKeyboardButton(text="Все объявления", callback_data="game_search")],
        [InlineKeyboardButton(text="Назад", callback_data="start_search")]
    ])

async def get_games_filter_search_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура для выбора игр"""
    builder = InlineKeyboardBuilder()
    
    for game in GAME_LIST:
        builder.add(InlineKeyboardButton(
            text=game,
            callback_data=f"filter_game_{game}"
        ))
    
    builder.adjust(2)

    builder.row(InlineKeyboardButton(text="Назад", callback_data="start_search"))
    return builder.as_markup()

# async def get_ranks_kb(game: str, with_back: bool = False) -> ReplyKeyboardMarkup:
#     keyboard = []
#     if game in GAMES_RANKS:
#         for rank in GAMES_RANKS[game]:
#             keyboard.append([KeyboardButton(text=rank)])
    
#     keyboard.append([KeyboardButton(text="Пропустить")])

#     if with_back:
#         keyboard.append([KeyboardButton(text="Назад")])
#     return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def get_goals_kb(with_back: bool = False) -> ReplyKeyboardMarkup:
    btns = [[KeyboardButton(text=goal)] for goal in GOALS_LIST]
    btns.append([KeyboardButton(text="Пропустить")])
    if with_back:
        btns.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True, one_time_keyboard=True)