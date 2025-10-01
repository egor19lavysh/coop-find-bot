from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.profile import Profile


async def get_profiles_kb(profiles: list[Profile]) -> InlineKeyboardBuilder:
    buider = InlineKeyboardBuilder()
    for profile in profiles:
        rating = round((profile.polite + profile.team_game + profile.skill) / 3, 1)
        buider.add(
            InlineKeyboardButton(
    text=f"{profile.nickname}, {profile.game} {str(rating) + "⭐" if rating != round(0.0, 1) else ""}".strip(),
                callback_data=f"read_profile_other_{profile.user_id}"
            )
        )

    ...