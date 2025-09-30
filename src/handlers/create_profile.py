from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository


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
    check_profile = State()
    is_active = State()

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
TEXT_PHOTO_ERROR = 'Пришлите либо фотографию профиля, либо напишите "Пропустите"'
TEXT_REPEAT_PROFILE = "Заполни заново свою анкету"
TEXT_ACCEPTED = "\n\nПодтвеждено ✅"
TEXT_REJECTED = "\n\nОтклонено ❌"
TEXT_ALREADY_HAVE_PROFILE = "Вы уже имеете анкету.\nВы можете ее удалить или изменить в меню /menu"
IS_PROFILE_OK = "Все верно?"

@router.message(Command("profile"))
async def start_profile(message: Message, state: FSMContext):
    if not await repository.get_profile(user_id=message.from_user.id):
        await state.update_data(user_id=message.from_user.id)
        await message.answer(text=TEXT_NICK)
        await state.set_state(ProfileForm.nickname)
    else:
        await message.answer(text=TEXT_ALREADY_HAVE_PROFILE)

@router.message(ProfileForm.nickname)
async def save_nickname(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(nickname=message.text)
        await message.answer(text=TEXT_TAG, reply_markup=await get_skip_keyboard())
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
                return
        
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb())
        await state.set_state(ProfileForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.gender)
    
@router.message(ProfileForm.game)
async def save_game(message: Message, state: FSMContext):
    if message.text:
        if message.text in GAME_LIST:
            await state.update_data(game=message.text)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(ProfileForm.game)
            return
        
        data = await state.get_data()
        await message.answer(text=TEXT_RANK.format(game=data["game"]), reply_markup=await get_skip_keyboard())
        await state.set_state(ProfileForm.rank)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.game)


@router.message(ProfileForm.rank)
async def save_rank(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Пропустить":
            await state.update_data(rank=None)
        else:
            await state.update_data(rank=message.text)
        
        await message.answer(text=TEXT_ABOUT, reply_markup=ReplyKeyboardRemove())
        await state.set_state(ProfileForm.about)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.rank)

@router.message(ProfileForm.about)
async def save_about(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(about=message.text)
        await message.answer(text=TEXT_GOAL)
        await state.set_state(ProfileForm.goal)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.about)

@router.message(ProfileForm.goal)
async def save_goal(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(goal=message.text)
        await message.answer(text=TEXT_PHOTO, reply_markup=await get_skip_keyboard())
        await state.set_state(ProfileForm.photo)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.goal)

@router.message(ProfileForm.photo)
async def save_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    elif message.text == "Пропустить":
        await state.update_data(photo=None)
    else:
        await message.answer(text=TEXT_PHOTO_ERROR)
        await state.set_state(ProfileForm.photo)
        return
    await check_profile(message=message, state=state)

async def check_profile(message: Message, state: FSMContext):
    data = await state.get_data()

    nickname = data["nickname"]
    telegram_tag = data["telegram_tag"] if data["telegram_tag"] else "Нет"
    gender = data["gender"] if data["gender"] else "Нет"
    game = data["game"]
    rank = data["rank"] if data["rank"] else "Нет"
    about = data["about"]
    goal = data["goal"]
    photo = data["photo"]

    if photo:
        try:
            await message.answer_photo(
                photo=photo,
                caption=PROFILE_SAMPLE.format(
                    nickname=nickname,
                    telegram_tag=telegram_tag,
                    gender=gender,
                    game=game,
                    rank=rank,
                    about=about,
                    goal=goal
                )
            )
        except:
            await message.answer(
                text=PROFILE_SAMPLE.format(
                    nickname=nickname,
                    telegram_tag=telegram_tag,
                    gender=gender,
                    game=game,
                    rank=rank,
                    about=about,
                    goal=goal
                ) + PHOTO_SAMPLE
            )
    else:
        await message.answer(
                text=PROFILE_SAMPLE.format(
                    nickname=nickname,
                    telegram_tag=telegram_tag,
                    gender=gender,
                    game=game,
                    rank=rank,
                    about=about,
                    goal=goal
                ) + PHOTO_SAMPLE
            )
        
    await message.answer(text=IS_PROFILE_OK, reply_markup=await get_commit_profile_kb())
    await state.set_state(ProfileForm.check_profile)

@router.message(ProfileForm.check_profile)
async def commit_profile(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Верно ✅":
            await message.answer(text=TEXT_SUCCESS, reply_markup=ReplyKeyboardRemove())
            await state.set_state(ProfileForm.is_active)
            await message.answer(text=TEXT_ALLOW_INVITATIONS, reply_markup=(await get_status_kb()).as_markup())
        elif message.text == "Неверно ❌":
            await message.answer(text=TEXT_REPEAT_PROFILE)
            await state.clear()
            await start_profile(message, state)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(ProfileForm.check_profile)
        
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(ProfileForm.check_profile)


@router.callback_query(ProfileForm.is_active)
async def save_status(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split("_")[-1]
    if status == "true":
        await state.update_data(is_active=True)
    elif status == "false":
        await state.update_data(is_active=False)
    else:
        await callback.message.answer(text=TEXT_WRONG_ANSWER)
        await state.set_state(ProfileForm.is_active)
        return

    await callback.bot.edit_message_reply_markup(
    chat_id=callback.message.chat.id,
    message_id=callback.message.message_id,
    reply_markup=None
    )

    await callback.message.edit_text(text=TEXT_ALLOW_INVITATIONS + TEXT_ACCEPTED if status == "true" else TEXT_REJECTED)
    
    await save_profile(message=callback.message, state=state)


async def save_profile(message: Message, state: FSMContext):
    data = await state.get_data()

    await repository.create_profile(
        user_id = data["user_id"],
        nickname = data["nickname"],
        game = data["game"],
        about = data["about"],
        goal = data["goal"],
        is_active = data["is_active"],
        telegram_tag = data["telegram_tag"],
        gender = data["gender"],
        rank = data["rank"],
        photo = data["photo"]
    )

    await state.clear()

