# handlers/edit_profile.py
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository
from utils.decorators import require_profile
from handlers.profile_states import *


router = Router()



TEXT_CHOOSE_FIELD = "Выбери поле, которое хочешь изменить:"
TEXT_EDIT_NICKNAME = "Введи новый никнейм:"
TEXT_EDIT_TAG = "Введи новый тег Telegram:"
TEXT_EDIT_GENDER = "Выбери новый пол:"
TEXT_EDIT_GAMES = "Выбери игры для редактирования:"
TEXT_EDIT_ABOUT = "Введи новое описание о себе:"
TEXT_EDIT_GOAL = "Введи новую цель поиска:"
TEXT_EDIT_PHOTO = "Отправь новое фото профиля:"
TEXT_EDIT_STATUS = "Изменить статус анкеты:"
TEXT_SUCCESS_EDIT = "Изменения успешно сохранены! ✅"
TEXT_SUCCESS = "Отлично! Твоя анкета успешно создана и теперь доступна другим игрокам. 👾"
TEXT_ALLOW_INVITATIONS = "Разрешить присылать приглашения в игру от других пользователей? При отклонении ты сможешь отправлять сообщения самостоятельно. "
TEXT_SKIP = '\n\n<i>Если не хочешь заполнять эту информацию, напиши в чат "Пропустить"</i>'
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_WRONG_ANSWER = "Выберите ответ из предложенного списка!"
TEXT_PHOTO_ERROR = 'Пришлите фотографию профиля или выберите доступный вариант ответа ("Фото с профиля" или "Пропустить")'
TEXT_REPEAT_PROFILE = "Заполни заново свою анкету"
TEXT_ACCEPTED = "\n\nПодтвеждено ✅"
TEXT_REJECTED = "\n\nОтклонено ❌"
TEXT_ALREADY_HAVE_PROFILE = "У тебя уже есть анкета.\nТы можешь ее удалить или изменить в меню /menu"
IS_PROFILE_OK = "Все верно?"
TEXT_RANK = "Укажи свой ранг/уровень в {game}:"
TEXT_ADD_GAME = "Добавить еще игру?"
TEXT_GAME = "Выбери игры, в которую ищешь тиммейтов:"



@router.callback_query(F.data == "edit_profile")
@require_profile
async def start_edit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await state.update_data(
        games = {}
    )
    
    await callback.message.answer(TEXT_CHOOSE_FIELD, reply_markup=await get_edit_fields_kb())
    await state.set_state(EditProfileForm.choose_field)
    await callback.answer()

async def start_edit_profile_message(message: Message, state: FSMContext):
    data = await state.get_data()


    if "process" in data and data["process"] == "creating_profile":
        pass
    else:
        await state.update_data(
        games = {}
    )
    
    await message.answer(TEXT_CHOOSE_FIELD, reply_markup=await get_edit_fields_kb())
    await state.set_state(EditProfileForm.choose_field)



@router.callback_query(EditProfileForm.choose_field)
@require_profile
async def process_field_selection(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[-1]
    
    await callback.answer()
    await callback.message.delete()
    
    if field == "nickname":
        await callback.message.answer(TEXT_EDIT_NICKNAME)
        await state.set_state(EditProfileForm.nickname)
    
    elif field == "tag":
        await callback.message.answer(TEXT_EDIT_TAG, reply_markup=await get_tag_kb(False))
        await state.set_state(EditProfileForm.telegram_tag)
    
    elif field == "gender":
        await callback.message.answer(TEXT_EDIT_GENDER, reply_markup=await get_gender_keyboard(False))
        await state.set_state(EditProfileForm.gender)
    
    elif field == "games":
        await callback.message.answer(TEXT_EDIT_GAMES, reply_markup=await get_game_kb(False))
        await state.set_state(EditProfileForm.games)
    
    elif field == "about":
        await callback.message.answer(TEXT_EDIT_ABOUT)
        await state.set_state(EditProfileForm.about)
    
    elif field == "goal":
        await callback.message.answer(TEXT_EDIT_GOAL)
        await state.set_state(EditProfileForm.goal)
    
    elif field == "photo":
        await callback.message.answer(TEXT_EDIT_PHOTO, reply_markup=await get_photo_kb(False))
        await state.set_state(EditProfileForm.photo)

### ХЕНДЛЕРЫ ДЛЯ ОБНОВЛЕНИЯ КОНКРЕТНЫХ ПОЛЕЙ

@router.message(EditProfileForm.nickname)
@require_profile
async def update_nickname(message: Message, state: FSMContext):
    if message.text:
        await repository.update_nickname(user_id=message.from_user.id, nickname=message.text)

        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(nickname=message.text)
            await message.answer(TEXT_SUCCESS_EDIT)
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())

    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.message(EditProfileForm.telegram_tag)
@require_profile
async def update_telegram_tag(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Пропустить":
            telegram_tag = None
        elif message.text == "Отправить данные":
            telegram_tag = message.from_user.username
        else:
            telegram_tag = message.text
        
        await repository.update_telegram_tag(user_id=message.from_user.id, telegram_tag=telegram_tag)
        data = await state.get_data(telegram_tag=telegram_tag)
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data()
            await message.answer(TEXT_SUCCESS_EDIT)
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())
    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.message(EditProfileForm.gender)
@require_profile
async def update_gender(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Пропустить":
            gender = None
        elif message.text in GENDER_LIST:
            gender = message.text
        else:
            await message.answer(TEXT_WRONG_ANSWER)
            return
        
        await repository.update_gender(user_id=message.from_user.id, gender=gender)
        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(gender=gender)
            await message.answer(TEXT_SUCCESS_EDIT)
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())
    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.message(EditProfileForm.about)
@require_profile
async def update_about(message: Message, state: FSMContext):
    if message.text:
        await repository.update_about(user_id=message.from_user.id, about=message.text)
        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(about=message.text)
            await message.answer(TEXT_SUCCESS_EDIT)
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())
    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.message(EditProfileForm.goal)
@require_profile
async def update_goal(message: Message, state: FSMContext):
    if message.text:
        await repository.update_goal(user_id=message.from_user.id, goal=message.text)
        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(goal=message.text)
            await message.answer(TEXT_SUCCESS_EDIT)
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())
    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.message(EditProfileForm.photo)
@require_profile
async def update_photo(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Фото с профиля":
            photos = await message.bot.get_user_profile_photos(message.from_user.id)
            if photos.total_count > 0:
                photo = photos.photos[0][-1].file_id
            else:
                photo = None
        elif message.text == "Пропустить":
            photo = None
        else:
            await message.answer(TEXT_PHOTO_ERROR)
            return
    elif message.photo:
        photo = message.photo[-1].file_id
    else:
        await message.answer(TEXT_PHOTO_ERROR)
        return
    
    await repository.update_photo(user_id=message.from_user.id, photo=photo)
    data = await state.get_data()
    if "process" in data and data["process"] == "creating_profile":
        await state.update_data(photo=photo)
        await message.answer(TEXT_SUCCESS_EDIT)
        await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
    else:
        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())


@router.callback_query(EditProfileForm.games)
@require_profile
async def save_game(callback: CallbackQuery, state: FSMContext):
    game = callback.data.split("_")[-1]

    data = await state.get_data()
    games = data["games"]

    await callback.answer()

    if game:
        if game in GAME_LIST:
            if game not in games:
                await state.update_data(game=game)
            else:
                await callback.message.answer(text="Ты уже выбрал эту игру!")
                await callback.message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(False))
                await state.set_state(EditProfileForm.add_new_game)
                return
        else:
            await callback.message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(EditProfileForm.games)
            return
        
        await callback.message.answer(text=TEXT_RANK.format(game=game), reply_markup=await get_skip_keyboard(False))
        await state.set_state(EditProfileForm.rank)
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(EditProfileForm.games)
    
    


@router.message(EditProfileForm.rank)
async def save_rank(message: Message, state: FSMContext):
    if message.text:
        data = await state.get_data()
        games = data["games"]
        game = data["game"]

        if message.text == "Пропустить":
            rank = None
        else:
            rank = message.text

        games[game] = rank

        await state.update_data(
            games=games,
            game=None
        )
        
        await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(False))
        await state.set_state(EditProfileForm.add_new_game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(EditProfileForm.rank)


@router.message(EditProfileForm.add_new_game)
async def add_new_game(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Да":
            await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(False))
            await state.set_state(EditProfileForm.games)
        elif message.text == "Нет":
            data = await state.get_data()
            games = data["games"]
            await repository.update_games(user_id=message.from_user.id, games=games)

            data = await state.get_data()
            if "process" in data and data["process"] == "creating_profile":
                await state.update_data(games=games)
                await message.answer(TEXT_SUCCESS_EDIT)
                await message.answer("Вернуться к проверке анкеты?", 
                            reply_markup=await get_back_to_check_kb())
            else:
                await message.answer(TEXT_SUCCESS_EDIT, reply_markup=await get_back_to_menu())
        else:
            await message.answer(text=TEXT_WRONG_ANSWER)
            await state.set_state(EditProfileForm.add_new_game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(EditProfileForm.add_new_game)

@router.callback_query(F.data == "back_to_profile_check")
async def back_to_profile_check(callback: CallbackQuery, state: FSMContext):
    """Возврат к проверке анкеты после редактирования"""
    from handlers.create_profile import check_profile
    
    await state.set_state(ProfileForm.check_profile)
    await check_profile(callback.message, state)
    await callback.answer()