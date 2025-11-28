from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu_kb import *
from utils.constants import *




router = Router()


### ТЕКСТЫ
TEXT_INTRO = "А кто это у нас такой красивый и до сих пор играет сам? Давай исправим это 🔍"


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.delete()
    await message.answer(text=TEXT_INTRO, reply_markup=(await get_menu_keyboard()).as_markup())

@router.callback_query(F.data == "menu")
async def cmd_menu_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=TEXT_INTRO, reply_markup=(await get_menu_keyboard()).as_markup())
    await callback.answer()

