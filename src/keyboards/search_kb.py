from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile


async def get_profiles_kb(profiles: list[Profile], page: int = 0, per_page: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_profiles = profiles[start_idx:end_idx]
    
    for profile in current_profiles:
        sa = (profile.polite + profile.team_game + profile.skill) / 3
        rating = round(sa, 1)
        rating_text = f" {rating}⭐" if rating is not None else ""
        
        builder.add(
            InlineKeyboardButton(
                text=f"{profile.nickname}, {profile.game}{rating_text}".strip(),
                callback_data=f"read_profile_other_{profile.user_id}"
            )
        )
    
    profiles_count = len(current_profiles)
    sizes = []
    if profiles_count < per_page:
        for _ in range(profiles_count // 2):
            sizes.append(2)

    if profiles_count % 2 != 0:
        sizes.append(1)
    
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
            callback_data="close_profiles_list"
        )
    )
    
    return builder.as_markup()

async def get_back_kb(game: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_profiles"
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
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_clans_kb(clans, page=0, per_page=2):
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
    
    # Навигация
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
            callback_data="close_clans_list"
        )
    )

    return builder.as_markup()

async def get_clan_detail_kb(clan_id: int, game: str) -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра клана"""
    buttons = [
        [InlineKeyboardButton(
            text="Вступить в клан",
            callback_data=f"join_clan_{clan_id}"
        )],
        [InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_clans"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# keyboards/search_kb.py
async def get_back_kb(game: str, search_type: str = "profiles") -> InlineKeyboardMarkup:
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