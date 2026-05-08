from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import date, timedelta, datetime
import asyncio




class UtmTrackingMiddleware(BaseMiddleware):
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
        
        if last_activity_day := await statistic.get_last_activity_day(user.id):
            today = date.today()
            diff = (today - last_activity_day.date()).days

            if diff >= 1:
                asyncio.create_task(statistic.set_last_activity_day(event.from_user.id, datetime.now()))
        else:
            asyncio.create_task(statistic.set_last_activity_day(event.from_user.id, datetime.now()))

        return await handler(event, data)