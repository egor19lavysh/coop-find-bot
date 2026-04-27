from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import date, timedelta
from sqlalchemy.orm import Session
from repositories.profile_repository import profile_repository as pr
from utils.level_up import level_up

TEXT_ACTIVATION_SUCCESS = """
Ура! Твоя анкета снова активирована. Теперь тебя снова видят и 
могут приглашать 🎉
 
Удачи в поиске тиммейтов 😌
"""

class InactiveMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, CallbackQuery) and event.data == "activate_inactive_profile":
            return await handler(event, data)

        user_id = event.from_user.id
        if profile := await pr.get_profile(user_id=user_id):
            if not profile.is_active and profile.self_deactivated == False:
                await pr.activate_profile(user_id=user_id)
                await pr.update_self_deactivated(user_id=user_id, value=None)
                await pr.update_last_activity_day(user_id=user_id, day=date.today())
                try:
                    await event.bot.send_message(chat_id=user_id, text=TEXT_ACTIVATION_SUCCESS)
                except Exception as e:
                    print(f"Бот попытался отправить сообщение пользователю (id={user_id}) об активации профиля, но произошла ошибка:\n{e}")
        
        return await handler(event, data)