from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile_kb import *
from utils.constants import *
from repositories.clan_repository import clan_repository as repository
from handlers.menu import cmd_menu


router = Router()


class ClanForm(StatesGroup):
    name = State()
    game = State()
    description = State()
    demands = State()
    photo = State()
    check = State()

### ТЕКСТЫ
TEXT_NAME = "Введи название клана."
TEXT_GAME = "Выбери игру, в которую ищешь тиммейтов:"
TEXT_DESCRIPTION = "Введи описание клана."
TEXT_DEMANDS = "Введи требования для участия в клане."
TEXT_PHOTO = "Отправь фото профиля."
TEXT_ALREADY_HAVE_CLAN = "У тебя уже есть клан.\nТы можешь его удалить или изменить в меню /menu"
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_WRONG_ANSWER = "Выберите ответ из предложенного списка!"
TEXT_PHOTO_ERROR = 'Пришлите либо фотографию профиля, либо напишите "Пропустите"'
TEXT_REPEAT_PROFILE = "Заполни заново анкету своего клана"
TEXT_ACCEPTED = "\n\nПодтвеждено ✅"
TEXT_REJECTED = "\n\nОтклонено ❌"
IS_CLAN_OK = "Все верно?"
TEXT_SUCCESS = "Отлично! Анкета твоего клана успешно создана и теперь доступна другим игрокам. 👾"


@router.message(Command("clan"))
async def start_clan_with_message(message: Message, state: FSMContext):
    await state.update_data(
        user_id=message.from_user.id
    )
    await start_clan(message.bot, state=state)

async def start_clan(bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]

    if not await repository.get_clan(user_id=user_id):
        await bot.send_message(chat_id=user_id, text=TEXT_NAME)
        await state.set_state(ClanForm.name)
    else:
        await bot.send_message(chat_id=user_id, text=TEXT_ALREADY_HAVE_CLAN)

@router.message(ClanForm.name)
async def save_name(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(name=message.text)
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb())
        await state.set_state(ClanForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.name)

@router.message(ClanForm.game)
async def save_game(message: Message, state: FSMContext):
    if message.text:
        if message.text in GAME_LIST:
            await state.update_data(game=message.text)
            await message.answer(text=TEXT_DESCRIPTION, reply_markup=ReplyKeyboardRemove())
            await state.set_state(ClanForm.description)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(ClanForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.game)

@router.message(ClanForm.description)
async def save_description(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(description=message.text)
        await message.answer(text=TEXT_DEMANDS)
        await state.set_state(ClanForm.demands)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.description)

@router.message(ClanForm.demands)
async def save_demands(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(demands=message.text)
        await message.answer(text=TEXT_PHOTO, reply_markup=await get_skip_keyboard())
        await state.set_state(ClanForm.photo)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.demands)

@router.message(ClanForm.photo)
async def save_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    elif message.text == "Пропустить":
        await state.update_data(photo=None)
    else:
        await message.answer(text=TEXT_PHOTO_ERROR)
        await state.set_state(ClanForm.photo)
        return
    
    await check_profile(message=message, state=state)

async def check_profile(message: Message, state: FSMContext):
    data = await state.get_data()

    name = data["name"]
    game = data["game"]
    description = data["description"]
    demands = data["demands"]
    photo = data["photo"]

    if photo:
        await message.answer_photo(
            photo=photo,
            caption=CLAN_SAMPLE.format(
                name=name,
                game=game,
                description=description,
                demands=demands,
            )
        )

    else:
        await message.answer(
            text=CLAN_SAMPLE.format(
                name=name,
                game=game,
                description=description,
                demands=demands,
            ) + PHOTO_SAMPLE
        )

    await message.answer(text=IS_CLAN_OK, reply_markup=await get_commit_profile_kb())
    await state.set_state(ClanForm.check)


@router.message(ClanForm.check)
async def commit_profile(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Верно ✅":
            await message.answer(text=TEXT_SUCCESS, reply_markup=ReplyKeyboardRemove())
            await save_clan(message, state)
        elif message.text == "Неверно ❌":
            await message.answer(text=TEXT_REPEAT_PROFILE)
            await state.clear()
            await start_clan_with_message(message, state)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(ClanForm.check)
        
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.check.check_profile)

async def save_clan(message: Message, state: FSMContext):
    data = await state.get_data()

    name = data["name"]
    game = data["game"]
    description = data["description"]
    demands = data["demands"]
    photo = data["photo"]

    await repository.create_clan(
        user_id=message.from_user.id,
        name=name,
        game=game,
        description=description,
        demands=demands,
        photo=photo,
    )

    await state.clear()
    await cmd_menu(message)