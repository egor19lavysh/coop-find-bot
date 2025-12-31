from aiogram import Bot, types, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command, CommandObject
from keyboards.start_kb import get_start_keyboard
from utils.check_subscription import check_subscription
from handlers.profile.create_profile import start_profile
from aiogram.fsm.context import FSMContext
from config import settings
from statistic import Statistic
import asyncio
from repositories.user_repository import user_repository
from datetime import datetime


router = Router()

### ТЕКСТЫ
TEXT_START = ("Салют, игрок!🔥\n"
             "Готов найти тимейтов? Тогда создадим твою анкету. "
             "Напиши свой никнейм, который будет отображаться в анкете")


@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject, state: FSMContext, statistic: Statistic):
    builder = get_start_keyboard(user_id=message.from_user.id)
    await message.answer(text=TEXT_START)

    user_id = message.from_user.id
    chat_id = message.chat.id
    utm_label = command.args or 'None'
    if not (await user_repository.get_user(user_id)):
        await user_repository.add_user(user_id=user_id,
                                   username=message.from_user.username,
                                   first_name=message.from_user.first_name,
                                   last_name=message.from_user.last_name,
                                   utm_label=utm_label)

    asyncio.create_task(statistic.add_row(user_id=user_id,
                                          username=message.from_user.username,
                                          utm_label=utm_label,
                                          created_at=datetime.now()))
    
    await state.update_data(
            user_id=user_id,
            chat_id=chat_id
        )
    await start_profile(bot=message.bot, state=state)

# @router.callback_query(F.data.startswith("check_sub"))
# async def check_user_subscription(callback: CallbackQuery, state: FSMContext):
#     user_id = int(callback.data.split("_")[-1])
#     if await check_subscription(bot=callback.bot, user_id=user_id):
#         await callback.message.edit_text(text=callback.message.text)
#         await callback.message.answer(text=TEXT_SUB_SUCCESS)
#         await state.update_data(
#             user_id=user_id,
#             chat_id=callback.message.chat.id
#         )
#         await start_profile(bot=callback.bot, state=state)
#     else:
#         await callback.message.answer(text=TEXT_SUB_FAIL)
#         await callback.answer()

