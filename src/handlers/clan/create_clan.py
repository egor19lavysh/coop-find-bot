from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.profile_kb import *
from keyboards.clan_kb import get_commit_clan_kb
from utils.constants import *
from repositories.clan_repository import clan_repository as repository
from handlers.menu import cmd_menu
from states.create_clan import *
from utils.creation_process import CMDS, restrict_access
from typing import Union
from html import escape


router = Router()


### ТЕКСТЫ
TEXT_INTRO = "Чтобы разместить анкету клана ответь пожалуйста на пару вопросов ниже:"
TEXT_NAME = "Введи название клана."
TEXT_GAME = "Выбери игру, в которую ищешь тиммейтов:"
TEXT_DESCRIPTION = """
Введите описание вашего клана 🏰
В описании укажите кластер и сервер, на котором расположен клан, а также основные достижения и особенности клана. 

❗️На этом этапе не нужно писать требования к вступлению, они будут указываться в следующем шаге
"""
TEXT_DEMANDS = "Введи требования для участия в клане."
TEXT_PHOTO = "Отправь аватарку клана."
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_WRONG_ANSWER = "Выберите ответ из предложенного списка!"
TEXT_PHOTO_ERROR = 'Пришлите либо фотографию профиля, либо напишите "Пропустите"'
TEXT_REPEAT_PROFILE = "Заполни заново анкету своего клана"
TEXT_ACCEPTED = "\n\nПодтвеждено ✅"
TEXT_REJECTED = "\n\nОтклонено ❌"
IS_CLAN_OK = "Все верно?"
TEXT_SUCCESS = "Отлично! Анкета твоего клана успешно создана и теперь доступна другим игрокам. 👾"


@router.callback_query(F.data == "create_clan")
async def start_clan_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    
    await state.update_data(
        user_id=callback.from_user.id
    )
    await callback.answer()
    await start_clan(callback.bot, state=state)

async def start_clan(bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]

    await state.set_state(ClanForm.name)
    await bot.send_message(chat_id=user_id, text=TEXT_INTRO)
    await bot.send_message(chat_id=user_id, text=TEXT_NAME, reply_markup= await get_back_kb())
    

@router.message(ClanForm.name)
async def save_name(message: Message, state: FSMContext):
    if  message.text in CMDS:
        await restrict_access(message, TEXT_NAME, None)
        return
    
    if message.text:
        if message.text.strip().lower() == "назад":
            await message.answer("Создание анкеты отменено.", reply_markup=await get_back_to_menu())
            await state.clear()
            return
        
        await state.update_data(name=message.text)
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ClanForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.name)

@router.message(ClanForm.game)
@router.callback_query(ClanForm.game)
async def save_game(event: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, TEXT_GAME, get_game_kb, with_back=False)
            return
    else:
        callback = event

    if callback.data == "back_from_games":
        await callback.message.delete()
        await callback.message.answer(text=TEXT_NAME, reply_markup=await get_back_kb())
        await state.set_state(ClanForm.name)
        return

    game = callback.data.split("_")[-1]
    await callback.answer()

    if game:

        if game in GAME_LIST:
            await state.update_data(game=game)
            await callback.message.edit_text(text=f"Выбрана игра: {game}", reply_markup=None)

            if game == "Raven 2":
                from utils.raven import SERVER_TEXT
                await callback.message.answer(text=SERVER_TEXT, reply_markup=await get_raven_servers_kb(with_back=True))
                await state.set_state(ClanForm.raven_server)
            elif game == "Lineage 2M":
                from utils.lineage import SERVER_TEXT
                await callback.message.answer(text=SERVER_TEXT, reply_markup=await get_lineage_servers_pt_1(with_back=True))
                await state.set_state(ClanForm.lineage_server)
            else:
                await state.set_state(ClanForm.description)
                await callback.message.answer(text=TEXT_DESCRIPTION, reply_markup=ReplyKeyboardRemove())
        else:
            await state.set_state(ClanForm.game)
            await callback.message.answer(text=TEXT_WRONG_ANSWER)
            
    else:
        await state.set_state(ClanForm.game)
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        

@router.message(ClanForm.description)
async def save_description(message: Message, state: FSMContext):
    if message.text in CMDS:
        await restrict_access(message, TEXT_DESCRIPTION, ReplyKeyboardRemove)
        return
    
    if message.text:
        await state.update_data(description=message.text)
        await state.set_state(ClanForm.demands)
        await message.answer(text=TEXT_DEMANDS)
        
    else:
        await state.set_state(ClanForm.description)
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        

@router.message(ClanForm.demands)
async def save_demands(message: Message, state: FSMContext):
    if message.text in CMDS:
        await restrict_access(message, TEXT_DEMANDS, None)
        return
    
    if message.text:
        await state.update_data(demands=message.text)
        await state.set_state(ClanForm.photo)
        await message.answer(text=TEXT_PHOTO, reply_markup=await get_skip_keyboard(with_back=False))
        
    else:
        await state.set_state(ClanForm.demands)
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        

@router.message(ClanForm.photo)
async def save_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    elif message.text:
        if message.text in CMDS:
            await restrict_access(message, TEXT_PHOTO, get_skip_keyboard, with_back=False)
            return
        elif message.text.lower() == "пропустить":
            await state.update_data(photo=None)
    else:
        await state.set_state(ClanForm.photo)
        await message.answer(text=TEXT_PHOTO_ERROR)
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
            ),
            reply_markup=ReplyKeyboardRemove()
        )

    else:
        await message.answer(
            text=CLAN_SAMPLE.format(
                name=name,
                game=game,
                description=description,
                demands=demands,
            ) + PHOTO_SAMPLE,
            reply_markup=ReplyKeyboardRemove()
        )

    await message.answer(text=IS_CLAN_OK, reply_markup=await get_commit_clan_kb())
    await state.set_state(ClanForm.check)

@router.message(ClanForm.check)
@router.callback_query(ClanForm.check)
async def commit_profile(event: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, IS_CLAN_OK, get_commit_clan_kb)
            return
    else:
        callback = event

    await callback.answer()

    if callback.data:
        if callback.data == "clan_correct":
            await callback.message.answer(text=TEXT_SUCCESS, reply_markup=ReplyKeyboardRemove())
            await save_clan(callback.message, state, user_id=callback.from_user.id)
        elif callback.data == "clan_incorrect":
            await callback.message.answer(text=TEXT_REPEAT_PROFILE)
            await state.clear()
            await state.update_data(user_id=callback.from_user.id)
            await start_clan(callback.bot, state)
        else:
            await callback.message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(ClanForm.check)
        
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ClanForm.check)



async def save_clan(message: Message, state: FSMContext, user_id: int):
    data = await state.get_data()

    name = escape(data["name"])
    game = escape(data["game"])
    description = escape(data["description"])
    demands = escape(data["demands"])
    photo = escape(data["photo"])

    await repository.create_clan(
        user_id=user_id,
        name=name,
        game=game,
        description=description,
        demands=demands,
        photo=photo,
    )

    await state.clear()
    await cmd_menu(message)