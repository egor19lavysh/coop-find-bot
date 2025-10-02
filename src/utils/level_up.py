from aiogram import Bot


async def level_up(bot: Bot, user_id: int, new_level: int):
    await bot.send_message(
        chat_id=user_id,
        text=f"Твой уровень повышен! Теперь у тебя уровень {new_level}!🔥"
    )