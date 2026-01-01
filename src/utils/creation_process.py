from typing import Union, Callable, Coroutine
from aiogram.types import Message, CallbackQuery


CMDS = ["/menu", "/profile", "/clan", "/search"]

async def restrict_access(event: Union[Message, CallbackQuery], text: str, markup: Union[Callable, Coroutine] = None, *args, **kwargs):
    if isinstance(event, CallbackQuery):
        event = event.message

    await event.answer("Заполни анкету, чтобы получить доступ к меню📄")
    await event.answer(text, reply_markup=await markup(*args, **kwargs) if markup else None)
        
    