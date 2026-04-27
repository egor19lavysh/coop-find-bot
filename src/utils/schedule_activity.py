from repositories.profile_repository import profile_repository
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from models.profile import Profile
from datetime import datetime
from models.profile import Game


TEXT_14_DAYS = """
Салют! Твоя анкета была неактивна уже 14 дней поэтому сейчас другие пользователи тебя не видят и не могут пригласить в игру💔

Но ты можешь её вернуть! Просто нажми “Активировать ✅” ниже 👇
"""

TEXT_WARNING = """
Привет! От тебя давно не было активности 😒

❤️ Посмотри несколько анкет чтобы ничего не пропустить. 
Тимсик скрывает неактивные анкеты чтобы повысить шанс ответа при приглашении в игру.
"""


async def check_games(games: list[Game]) -> bool:
    games_str = set(game.name for game in games)
    skip_games = set(('Raid Shadow Legends', 'Lineage 2M', 'Raven 2', 'WoR'))
    return games_str.intersection(skip_games)


async def deactivate_inactive_profiles(bot: Bot):
    profiles: list[Profile] = await profile_repository.get_profiles()
    curr_date = datetime.now().date()

    for profile in profiles:
        print(f"Проверяем профиль пользователя (id={profile.user_id}) на неактивность. Последняя активность была {profile.last_activity_day}, сейчас {curr_date}.")
        if not (await check_games(profile.games)):
            if profile.is_active and (curr_date - profile.last_activity_day).days >= 5:
                await profile_repository.deactivate_profile(user_id=profile.user_id)
                await profile_repository.update_self_deactivated(user_id=profile.user_id, value=False)
                print(f"Профиль пользователя (id={profile.user_id}) был неактивен 5 дней, бот деактивировал его и попытался отправить сообщение с предупреждением.")
                try:
                    await bot.send_message(chat_id=profile.user_id, text=TEXT_WARNING)
                except Exception as e:
                    print(f"Бот попытался отправить сообщение пользователю (id={profile.user_id}) о неактивности 5 дней, но произошла ошибка:\n{e}")


async def send_message_to_inactive_profiles(bot: Bot):
    profiles: list[Profile] = await profile_repository.get_profiles()
    curr_date = datetime.now().date()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Активировать✅", callback_data="activate_inactive_profile")]
    ])

    for profile in profiles:
        if (curr_date - profile.last_activity_day).days == 14:
            try:
                await bot.send_message(chat_id=profile.user_id, text=TEXT_14_DAYS, reply_markup=markup)
            except Exception as e:
                print(f"Бот попытался отправить сообщение пользователю (id={profile.user_id}) о неактивности 14 дней, но произошла ошибка:\n{e}")
            