import asyncio
from aiogram import Bot, Dispatcher
from config import settings
import logging
from handlers import routers
from middleware import SubscriptionMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

# Run the bot
async def main() -> None:
    bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    for router in routers:
        dp.include_router(router)

    dp.message.middleware(SubscriptionMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
          