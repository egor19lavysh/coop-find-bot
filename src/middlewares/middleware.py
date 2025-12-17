from typing import Callable, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from utils.check_subscription import check_subscription
from keyboards.start_kb import get_start_keyboard



class SubscriptionMiddleware(BaseMiddleware):
    
    ALLOWED_COMMANDS = ['/start']
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        
        message = await self._get_message(event)
        if not message or not message.from_user:
            return await handler(event, data)
        
        user_id = message.from_user.id
        
        if not await self._should_check_subscription(event, message):
            return await handler(event, data)
        
        if not await check_subscription(bot=message.bot, user_id=user_id):
            builder = get_start_keyboard(user_id=user_id)
            #await message.answer(text=TEXT_SUB_FAIL, reply_markup=builder.as_markup())
            return
        
        return await handler(event, data)
    
    async def _get_message(self, event: TelegramObject) -> Message | None:
        """Безопасно получает сообщение из события"""
        if isinstance(event, Message):
            return event
        elif isinstance(event, CallbackQuery) and event.message:
            return event.message
        return None
    
    async def _should_check_subscription(self, event: TelegramObject, message: Message) -> bool:
        """Определяет, нужно ли проверять подписку для этого события"""

        if (isinstance(event, Message) and 
            message.text and 
            any(message.text.startswith(cmd) for cmd in self.ALLOWED_COMMANDS)):
            return False

        
        return True