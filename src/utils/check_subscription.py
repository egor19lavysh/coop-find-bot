from aiogram import Bot, types, Dispatcher


async def check_subscription(bot: Bot, user_id: int) -> bool:
    user = await bot.get_chat_member(chat_id="@ggstore_hub", user_id=user_id)
    return user.status != "left"