from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.estimate import ask_connect
from datetime import datetime
from aiogram.fsm.context import FSMContext


async def schedule_estimate(apscheduler: AsyncIOScheduler,
                            time: datetime,
                            bot: Bot, 
                            user_id: int,
                            teammate: str,
                            teammate_id: int,
                            state: FSMContext):
    apscheduler.add_job(
            ask_connect,
            trigger="date",
            run_date=time,
            kwargs={
                "bot": bot,
                "user_id": user_id,
                "teammate": teammate,
                "teammate_id": teammate_id,
                "state": state
            }
        )
