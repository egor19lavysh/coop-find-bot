from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile


async def get_profiles_kb(profiles: list[Profile], page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_profiles = profiles[start_idx:end_idx]
    
    for profile in current_profiles:
        sa = (profile.polite + profile.team_game + profile.skill) / 3
        print(sa)
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