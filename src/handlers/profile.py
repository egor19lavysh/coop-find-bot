from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile_kb import *
from utils.constants import *



router = Router()

### ФОРМА ДЛЯ АНКЕТЫ
class ProfileForm(StatesGroup):
    nickname = State()
    telegram_tag = State()
    gender = State()
    game = State()
    rank = State()
    about = State()
    goal = State()
    photo = State()

### ТЕКСТЫ
TEXT_NICK = "Введи свой никнейм (он будет отображаться в анкете)."
TEXT_TAG = "Укажи свой тег в Telegram (по желанию)."
TEXT_GENDER = "Выбери свой пол."
TEXT_GAME = "Выбери игры, в которую ищешь тиммейтов:"
TEXT_RANK = "Укажи свой ранг/уровень в {game}:"
TEXT_ABOUT = "Расскажи немного о себе. Например, опиши свои интересы, опыт игры, укажи UID (по желанию):"
TEXT_GOAL = "Укажи свою цель поиска: (например: для общения, для буст рейтинга и т.д.)"
TEXT_PHOTO = "Отправь фото профиля." 
TEXT_SUCCESS = "Отлично! Твоя анкета успешно создана и теперь доступна другим игрокам. 👾"
TEXT_ALLOW_INVITATIONS = "Разрешить присылать приглашения от других пользователей?"
TEXT_SKIP = '\n\n<i>Если не хочешь заполнять эту информацию, напиши в чат "Пропустить"</i>'
TEXT_ANSWER_TYPE_ERROR = "Ответьте текстом!"
TEXT_WRONG_ANSWER = "Выберите ответ из предложенного списка!"

@router.message(Command("profile"))
async def start_profile(message: Message, state: FSMContext):
    await state.update_data(user_id=message.from_user.id)
    await message.answer(text=TEXT_NICK)
    await state.set_state(ProfileForm.nickname)

@router.message(ProfileForm.nickname)
async def save_nickname(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(nickname=message.text)
        await message.answer(text=TEXT_TAG + TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_skip_keyboard())
        await state.set_state(ProfileForm.telegram_tag)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.nickname)

@router.message(ProfileForm.telegram_tag)
async def save_telegram_tag(message: Message, state: FSMContext):
    
    if message.text:
        if message.text == "Пропустить":
            await state.update_data(telegram_tag=None)
        else:
            await state.update_data(telegram_tag=message.text)
        
        await message.answer(text=TEXT_GENDER, reply_markup=await get_gender_keyboard())
        await state.set_state(ProfileForm.gender)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.telegram_tag)

@router.message(ProfileForm.gender)
async def save_gender(message: Message, state: FSMContext):
    
    if message.text:
        if message.text == "Пропустить":
            await state.update_data(gender=None)
        else:
            if message.text in GENDER_LIST:
                await state.update_data(gender=message.text)
            else:
                await message.answer(text=TEXT_WRONG_ANSWER)
                await state.set_state(ProfileForm.gender)
        
        await message.answer(text=TEXT_GAME, reply_markup=ReplyKeyboardRemove())
        await state.set_state(ProfileForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.gender)
    
        
