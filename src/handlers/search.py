from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.constants import *
from keyboards.profile_kb import get_game_kb 
from keyboards.search_kb import get_profiles_kb, get_back_kb
from repositories.profile_repository import profile_repository as repository

router = Router()

class GameForm(StatesGroup):
    game = State()

class SendMessageForm(StatesGroup):
    message = State()

### ТЕКСТЫ
TEXT_INTRO = "Выбери игру."
TEXT_WRONG_NAME_GANE = "Выбери игру из предложенного списка"
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_NO_PROFILES = "Активных анкет по {game} не нашлось..."
TEXT_PROFILES_FOUND = "Сейчас ищут напарников:"
TEXT_SEND_MESSAGE = "Напиши пару ласковых этому фрукту"
TEXT_TRIED_TO_SEND_MESSAGE = "Бот попытался отправить сообщение, но что-то пошло не так..."
TEXT_SENT_MESSAGE = "Сообщение отправил. Ответ прилетит в личные сообщения."
TEXT_MESSAGE = "Пользователь {name} отправил тебе сообщение:\n\n{message}"
TEXT_ADDITIONAL_INFO = "\nЕго тег в телеграме - {tag}"
TEXT_INVITE = "Пользователь {name} приглашает тебя в {game}."

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
    profiles = await repository.get_profiles_by_game(game=game, user_id=message.from_user.id)
    
    if profiles:
        # Сохраняем профили в состояние для пагинации
        await state.clear() 
        await state.update_data(profiles=profiles, current_page=0, game=game)
        
        keyboard = await get_profiles_kb(profiles, page=0)
        await message.answer(
            text=TEXT_PROFILES_FOUND,
            reply_markup=keyboard
        )
    else:
        await message.answer(text=TEXT_NO_PROFILES.format(game=game))
        await state.clear()

@router.callback_query(F.data.startswith("get_profiles_by_"))
async def get_profiles_callback_handler(callback: CallbackQuery, state: FSMContext):
    game = callback.data.split("_")[-1]
    await callback.answer()
    await get_profiles_by_game(callback.message, state, game)

# Обработчик для пагинации
@router.callback_query(F.data.startswith("profiles_page_"))
async def handle_profiles_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    profiles = data.get("profiles", [])
    
    if profiles:
        await state.update_data(current_page=page)
        keyboard = await get_profiles_kb(profiles, page=page)
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()

# Обработчик для кнопки текущей страницы (ничего не делает)
@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery):
    await callback.answer()

# Обработчик для закрытия списка
@router.callback_query(F.data == "close_profiles_list")
async def close_profiles_list(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "back_to_profiles")
async def get_back_to_profiles(callback: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    game = data.get("game")
    
    if game:
        await callback.message.delete()
        # Восстанавливаем список профилей
        profiles = await repository.get_profiles_by_game(game=game, user_id=callback.from_user.id)
        if profiles:
            await state.update_data(profiles=profiles, current_page=0)
            keyboard = await get_profiles_kb(profiles, page=0)
            await callback.message.answer(
                text=TEXT_PROFILES_FOUND,
                reply_markup=keyboard
            )
    await callback.answer()

@router.callback_query(F.data.startswith("send_message_to_user_"))
async def send_message(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[-1])
    
    # Получаем текущие данные состояния (включая game)
    data = await state.get_data()
    game = data.get("game")
    
    await state.set_state(SendMessageForm.message)
    await state.update_data(
        user_id=user_id,
        game=game  # Сохраняем игру в состояние
    )
    await callback.message.answer(text=TEXT_SEND_MESSAGE)
    await callback.answer()

@router.message(SendMessageForm.message)
async def send_message_to_user(message: Message, state: FSMContext):
    if message.text:
        data = await state.get_data()
        user_id = data.get("user_id")
        game = data.get("game")
        
        if not user_id or not game:
            await message.answer(text="Произошла ошибка. Попробуйте заново.")
            await state.clear()
            return

        postfix = TEXT_ADDITIONAL_INFO.format(
                tag=message.from_user.username)
                
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=TEXT_MESSAGE.format(name=message.from_user.full_name, message=message.text) + postfix
            )
            await message.answer(text=TEXT_SENT_MESSAGE, reply_markup=await get_back_kb(game=game))
        except:
            await message.answer(text=TEXT_TRIED_TO_SEND_MESSAGE, reply_markup=await get_back_kb(game=game))
        
        # Очищаем состояние, но сохраняем игру для возможности вернуться
        await state.clear()
        await state.update_data(game=game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(SendMessageForm.message)

@router.callback_query(F.data.startswith("invite_user_"))
async def invite_user(callback: CallbackQuery, state: FSMContext):
    callback_parts = callback.data.split("_")
    user_id = int(callback_parts[-1])
    game = callback_parts[-2]

    postfix = TEXT_ADDITIONAL_INFO.format(
                tag="@" + callback.from_user.username)
    
    await state.update_data(game=game)
    
    try:
        await callback.bot.send_message(
                chat_id=user_id,
                text=TEXT_INVITE.format(name=callback.from_user.full_name, game=game) + postfix
            )
        await callback.message.answer(text=TEXT_SENT_MESSAGE, reply_markup=await get_back_kb(game=game))
    except Exception as e:
        await callback.message.answer(text=TEXT_TRIED_TO_SEND_MESSAGE, reply_markup=await get_back_kb(game=game))

    await callback.answer()




    
