from aiogram import Bot, types, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from keyboards.start_kb import get_start_keyboard
from utils.check_subscription import check_subscription
from config import settings


router = Router()

### ТЕКСТЫ
TEXT_START = "Привет, игрок! Прежде чем начать поиск тиммейтов — подпишись на наш хаб. Там ты найдешь свежие новости, мемы, розыгрыши."
TEXT_SUB_SUCCESS = " Отлично! Подписка подтверждена добро пожаловать в наше коммьюнити игроков 👾"
TEXT_SUB_FAIL = "Похоже, ты ещё не подписался на наш хаб. Это обязательный шаг, чтобы продолжить 💡"
TEXT_SUB_CHECKED = "\n\nПроверено✅"
###


@router.message(Command("start"))
async def cmd_start(message: Message):
    builder = get_start_keyboard(user_id=message.from_user.id)
    await message.answer(text=TEXT_START, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("check_sub"))
async def check_user_subscription(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    if await check_subscription(bot=callback.bot, user_id=user_id):
        await callback.message.edit_text(text=callback.message.text)
        await callback.message.answer(text=TEXT_SUB_SUCCESS)
    else:
        await callback.message.answer(text=TEXT_SUB_FAIL)
        await callback.answer()

@router.message(Command("test"))
async def cmd_test(message: Message):
    await message.answer("test")


