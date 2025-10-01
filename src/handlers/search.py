from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.constants import *
from keyboards.profile_kb import get_game_kb
from repositories.profile_repository import profile_repository as repository


router = Router()

class GameForm(StatesGroup):
    game = State()


### ТЕКСТЫ
TEXT_INTRO = "Выбери игру."
TEXT_WRONG_NAME_GANE = "Выбери игру из предложенного списка"
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_NO_PROFILES = "Активных анкет по {game} не нашлось..."

@router.callback_query(F.data == "start_search")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GameForm.game)
    await callback.message.answer(text=TEXT_INTRO, reply_markup=await get_game_kb())
    await callback.answer()

@router.message(GameForm.game)
async def save_game_name(message: Message, state: FSMContext):
    if message.text:
        if message.text in GAME_LIST:
            await get_profiles_by_game(message=message, state=state, game=message.text)
            return
        else:
            await message.answer(text=TEXT_WRONG_NAME_GANE)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)

    await state.set_state(GameForm.game)

async def get_profiles_by_game(message: Message, state: FSMContext, game: str):
    if profiles := repository.get_profiles_by_game(game=game):
        pass
    else:
        await message.answer(text=TEXT_NO_PROFILES.format(game=game))