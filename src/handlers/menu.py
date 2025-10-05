from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu_kb import *
from utils.constants import *




router = Router()


### ТЕКСТЫ
TEXT_INTRO = "А кто это у нас тут такой красивый и без тиммейта? Надо это исправить"


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(text=TEXT_INTRO, reply_markup=(await get_menu_keyboard()).as_markup())

@router.message(Command("remove_kb"))
async def remove_kb(message: Message):
    await message.answer(text="Клавиатура удалена.", reply_markup=ReplyKeyboardRemove())