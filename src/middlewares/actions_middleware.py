from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from repositories.profile_repository import profile_repository as repository
from repositories.user_repository import user_repository
from utils.level_up import level_up
import asyncio
from config import settings
from google_sheet import GoogleSheetService
from statistic import Statistic



class ActivityTrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        statistic = data.get('statistic')
        
        # Получаем пользователя из события
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        else:
            # Если это не Message и не CallbackQuery, пропускаем
            return await handler(event, data)
        

        if profile:= await repository.get_profile(user.id):
            
            today = date.today()
            last_activity_day = profile.last_activity_day
            diff = (today - last_activity_day).days

            if diff > 1:
                await repository.update_last_activity_day(user_id=user.id, day=today)
                await repository.update_days_series(user_id=user.id)
                asyncio.create_task(statistic.set_last_activity_day(event.from_user.id, datetime.now()))

                new_xp = profile.experience + 50
                if profile.experience // 100 < new_xp // 100:
                    await level_up(event.bot, user.id, new_xp // 100 + 1)
                await repository.add_experience(user_id=user.id, experience=50)

            elif diff == 1:
                if (profile.days_series + 1) % 5 == 0 and (profile.days_series + 1) > 0:
                    new_xp = profile.experience + 25
                    if profile.experience // 100 < new_xp // 100:
                        await level_up(event.bot, user.id, new_xp // 100 + 1)
                    await repository.add_experience(user_id=user.id, experience=25)
                
                new_xp = profile.experience + 50
                if profile.experience // 100 < new_xp // 100:
                    await level_up(event.bot, user.id, new_xp // 100 + 1)
                await repository.add_experience(user_id=user.id, experience=50)

                await repository.update_last_activity_day(user_id=user.id, day=today)
                await repository.update_days_series(user_id=user.id, days=profile.days_series + 1)
                asyncio.create_task(statistic.set_last_activity_day(event.from_user.id, datetime.now()))
        
        return await handler(event, data)