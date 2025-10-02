import asyncio
from aiogram import Bot, Dispatcher
from config import settings
import logging
from handlers import routers
from middlewares.middleware import SubscriptionMiddleware
from middlewares.apscheduler_middleware import SchedulerMiddleware
from middlewares.actions_middleware import ActivityTrackingMiddleware
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

# Run the bot
async def main() -> None:
    bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    for router in routers:
        dp.include_router(router)

    scheduler_middleware = SchedulerMiddleware(scheduler=scheduler)
    sub_middleware = SubscriptionMiddleware()
    action_middleware = ActivityTrackingMiddleware()

    dp.message.middleware(sub_middleware)
    dp.callback_query.middleware(sub_middleware)
    dp.message.middleware(scheduler_middleware)
    dp.callback_query.middleware(scheduler_middleware)
    dp.message.middleware(action_middleware)
    dp.callback_query.middleware(action_middleware)
    

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
          