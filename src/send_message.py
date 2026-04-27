import asyncio
import sys
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from repositories.user_repository import UserRepository
from database import AsyncSessionFactory

IMAGE = "AgACAgIAAxkBAAEFEC1p2sLRsssBxXECjM2pXeUC8DTatgACjxprG9bV2UrSa8UPZkXvYgEAAwIAA3kAAzsE"
TEXT = """
ИЩЕМ ДОБРОВОЛЬЦЕВ!

💻 Ищем людей, чтобы потыкать новый сайт.
Да, такие дела. Новый GG.Store почти готов, но перед релизом нужен краш-тест 🔥

Хочешь помочь нам стать лучше и получить за это презент?
Пиши в ЛС админу, (https://t.me/gg_store) выдадим доступ и скинем форму
"""

async def send_message_to_all_users():
    bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    user_repo = UserRepository(session_factory=AsyncSessionFactory)

    users = await user_repo.get_users()

    for user in users:
        try:
            await bot.send_photo(chat_id=user.user_id, photo=IMAGE, caption=TEXT)
            print(f"Сообщение отправлено пользователю {user.user_id}")
        except Exception as e:
            print(f"Ошибка отправки пользователю {user.user_id}: {e}")

    await bot.session.close()


if __name__ == "__main__":

    asyncio.run(send_message_to_all_users())