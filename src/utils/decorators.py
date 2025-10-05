from functools import wraps
from aiogram.types import Message, CallbackQuery
from typing import Union, Callable, Any
from repositories.profile_repository import profile_repository as repository


def require_profile(func: Callable) -> Callable:
    """
    Упрощенный декоратор для проверки профиля
    """
    @wraps(func)
    async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = event.from_user.id
        
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message
            await event.answer()
        else:
            return await func(event, *args, **kwargs)
        
        profile = await repository.get_profile(user_id=user_id)
        
        if not profile:
            await message.answer("У тебя еще нет анкеты. Создай ее с помощью /profile")
            return None
        
        return await func(event, *args, **kwargs)
    
    return wrapper