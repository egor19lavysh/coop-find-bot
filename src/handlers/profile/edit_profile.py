from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository
from utils.decorators import require_profile
from states.edit_profile import *
from states.create_profile import *




router = Router()



TEXT_CHOOSE_FIELD = "Выбери поле, которое хочешь изменить:"
TEXT_EDIT_NICKNAME = "Введи новый никнейм:"
TEXT_EDIT_TAG = """ \
Введи новый тег в Telegram без @

Если не хочешь, чтобы тебе писали в личку, просто пропусти этот шаг, нажав кнопку ниже💬
"""
TEXT_EDIT_GENDER = "Выбери новый пол:"
TEXT_EDIT_GAMES = "Выбери игры для редактирования:"
TEXT_EDIT_ABOUT = "Введи новое описание о себе:"
TEXT_EDIT_GOAL = "Выбери новую цель поиска:"
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
TEXT_TIME = "Выбери, пожалуйста, удобное время для игры по МСК:"
TEXT_WARCRAFT_MODE = "Выбери режим из списка, в котором хочешь указать рейтинг:"
TEXT_NUM_RANK = "Введи силу аккаунта числом:"
TEXT_GALLERY = "Отправь скриншоты игрового профиля, до 10 шт. (по желанию)"
TEXT_TIME = "Выбери, пожалуйста, удобное время для игры по МСК:"
TEXT_BACK_TO_MENU = "Вернуться назад?"
TEXT_RSL = """
Введи силу аккаунта в миллионах 🌟
Если сила меньше 1 млн — впиши дробное значение.

Пример: 500 000 тыс = 0,5 млн
"""
TEXT_PHOTO_COUNT_ERROR = "Пришлите 1 фотографию"
TEXT_BACK = "back"


@router.callback_query(F.data == "edit_profile")
@require_profile
async def start_edit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()

    await state.update_data(
        games = {},
        time = [],
        goals = []
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
        games = {},
        time = [],
        goals = []
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
        await state.set_state(EditProfileForm.games)
        await update_game(callback, state)

    elif field == "time":
        await callback.message.answer(TEXT_TIME, reply_markup=await get_time_kb(False))
        await state.set_state(EditProfileForm.time)
    
    elif field == "about":
        await callback.message.answer(TEXT_EDIT_ABOUT)
        await state.set_state(EditProfileForm.about)
    
    elif field == "goal":
        await callback.message.answer(TEXT_EDIT_GOAL, reply_markup=await get_goals_kb())
        await state.update_data(goals=[])
        await state.set_state(EditProfileForm.goal)
    
    elif field == "photo":
        await callback.message.answer(TEXT_EDIT_PHOTO, reply_markup=await get_photo_kb(False))
        await state.set_state(EditProfileForm.photo)

### ХЕНДЛЕРЫ ДЛЯ ОБНОВЛЕНИЯ КОНКРЕТНЫХ ПОЛЕЙ

@router.message(EditProfileForm.nickname)
@require_profile
async def update_nickname(message: Message, state: FSMContext):
    if message.text and len(message.text) <= 8:
        await repository.update_nickname(user_id=message.from_user.id, nickname=message.text)

        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(nickname=message.text)
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
            await state.clear()

    else:
        await message.answer("Напиши свой ник текстом (до 8 символов)")

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
        data = await state.update_data(telegram_tag=telegram_tag)
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data()
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
            await state.clear()

    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.callback_query(EditProfileForm.gender)
@require_profile
async def update_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    text = callback.data.split("_")[-1]

    if text:
        if text == "skip":
            gender = None
        elif text in GENDER_LIST:
            gender = text
        else:
            await callback.message.answer(TEXT_WRONG_ANSWER)
            return
        
        await repository.update_gender(user_id=callback.message.from_user.id, gender=gender)
        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(gender=gender)
            await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await callback.message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
            await state.set_state(EditProfileForm.clear)
        else:
            await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
            await state.clear()

    else:
        await callback.message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.callback_query(EditProfileForm.time)
@require_profile
async def update_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = callback.data.split("_")[-1]
    data = await state.get_data()
    time = data["time"]

    if text:
        if text in CONVENIENT_TIME:
            if text not in time:
                time.append(text)
                await state.update_data(time=time)
                await callback.message.edit_text(f"Выбрано время: {text}", reply_markup=None)
                await callback.message.answer(text="Добавить еще промежуток время?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(EditProfileForm.add_new_time)
            else:
                await callback.message.answer("Вы уже выбрали этот промежуток времени. Теперь выберите другой:", reply_markup=await get_time_kb(with_back=True))
        else:
            await callback.message.answer(text="Выбери промежуток времени из списка.")
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_time_kb(with_back=True))
    
@router.callback_query(EditProfileForm.add_new_time)
@require_profile
async def add_new_time(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    await callback.message.delete()
    text = callback.data.split("_")[-1]

    if text == TEXT_BACK:
        data = await state.get_data()
        time = data["time"]
        
        if time:
            time.pop()
            await state.update_data(time=time)
            
            if time:  # Если остались игры, возвращаемся к выбору добавления
                await callback.message.answer(text="Добавить еще промежуток времени?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(EditProfileForm.add_new_time)
            else:  # Если игр не осталось, возвращаемся к выбору первой игры
                await callback.message.answer(text=TEXT_TIME, reply_markup=await get_time_kb(with_back=False))
                await state.set_state(EditProfileForm.time)
        return
    
    if text:
        if text == "Да":
            await callback.message.answer(text=TEXT_TIME, reply_markup=await get_time_kb(with_back=False))
            await state.set_state(EditProfileForm.time)
        elif text == "Нет":
            time = data["time"]
            await repository.update_time(user_id=callback.from_user.id, time=time)

            if "process" in data and data["process"] == "creating_profile":
                await state.update_data(time=time)
                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                await callback.message.answer("Вернуться к проверке анкеты?", 
                            reply_markup=await get_back_to_check_kb())
                await state.set_state(EditProfileForm.clear)
            else:
                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                await state.clear()

        else:
            await callback.message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb())
            await state.set_state(EditProfileForm.add_new_time)
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb())
        await state.set_state(EditProfileForm.add_new_time)

@router.message(EditProfileForm.about)
@require_profile
async def update_about(message: Message, state: FSMContext):
    if message.text:
        await repository.update_about(user_id=message.from_user.id, about=message.text)
        data = await state.get_data()
        if "process" in data and data["process"] == "creating_profile":
            await state.update_data(about=message.text)
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
        else:
            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
            await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
            await state.clear()

    else:
        await message.answer(TEXT_ANSWER_TYPE_ERROR)

@router.callback_query(EditProfileForm.goal)
@require_profile
async def update_goal(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = callback.data.split("_")[-1]

    data = await state.get_data()
    goals = data["goals"]

    if text:
        if text in GOALS_LIST:
            if callback.message.text not in goals:
                goals.append(text)
                await state.update_data(goals=goals)
                await callback.message.edit_text(f"Выбрана цель: {text}", reply_markup=None)
                await callback.message.answer(text="Добавить еще цель?", reply_markup=await get_confirmation_kb(False))
                await state.set_state(EditProfileForm.add_new_goal)
            else:
                await callback.message.answer("Вы уже выбрали эту цель. Теперь выберите другую:", reply_markup=await get_goals_kb(with_back=False))
        else:
            await callback.message.answer(text="Выбери цель из списка.")
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_goals_kb(with_back=False))

@router.callback_query(EditProfileForm.add_new_goal)
@require_profile
async def add_new_goal(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    text = callback.data.split("_")[-1]

    await callback.message.delete()

    if text:
        if text == "Да":
            await callback.message.answer(text=TEXT_EDIT_GOAL, reply_markup=await get_goals_kb(with_back=False))
            await state.set_state(EditProfileForm.goal)
        elif text == "Нет":
            goals = data["goals"]
            await repository.update_goal(user_id=callback.from_user.id, goals=goals)

            if "process" in data and data["process"] == "creating_profile":
                await state.update_data(goals=goals)
                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                await callback.message.answer("Вернуться к проверке анкеты?", 
                            reply_markup=await get_back_to_check_kb())
                await state.set_state(EditProfileForm.clear)
                
            else:
                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                await state.clear()

        else:
            await callback.message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb(False))
            await state.set_state(EditProfileForm.add_new_goal)
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb(False))
        await state.set_state(EditProfileForm.add_new_goal)



@router.message(EditProfileForm.photo)
@require_profile
async def update_photo(message: Message, state: FSMContext):
    data = await state.get_data()
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
        # Проверяем, является ли это частью альбома
        if message.media_group_id:
            if data.get("msg_group_id", "") != message.media_group_id:
                await message.answer(TEXT_PHOTO_COUNT_ERROR, reply_markup=await get_photo_kb(with_back=True))
                await state.update_data(
                    msg_group_id=message.media_group_id
                )
                return
            else:
                return

        # Берём самую большую версию фото
        photo = message.photo[-1].file_id
    
    await repository.update_photo(user_id=message.from_user.id, photo=photo)
    data = await state.get_data()

    if "process" in data and data["process"] == "creating_profile":
        await state.update_data(photo=photo)
        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
        await message.answer("Вернуться к проверке анкеты?", 
                        reply_markup=await get_back_to_check_kb())
    else:
        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
        await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
        await state.clear()

    


@router.callback_query(F.data == "update_games")
async def update_games(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await update_game(callback, state)


async def update_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    games = await repository.get_games_by_user_id(user_id=callback.from_user.id)
    data = await state.get_data()
    if "process" in data and data["process"] == "creating_profile":
        await callback.message.answer("Ваши игры:", reply_markup=await get_edit_games_kb(games, process="creating_profile"))
    else:
        await callback.message.answer("Ваши игры:", reply_markup=await get_edit_games_kb(games, new_game=True))


@router.callback_query(F.data == "add_new_game")
async def create_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    all_games = GAME_LIST
    user_games = await repository.get_games_by_user_id(callback.from_user.id)
    user_game_names = {g.name for g in user_games}

    # Исключаем уже добавленные игры
    available_games = [game for game in all_games if game not in user_game_names]

    if not available_games:
        await callback.message.answer("Вы уже добавили все доступные игры.", reply_markup=await get_back_to_menu())
        return

    keyboard = InlineKeyboardBuilder()
    for game in available_games:
        keyboard.add(InlineKeyboardButton(text=game, callback_data=f"select_new_game_{game}"))
    keyboard.adjust(2)
    await callback.message.answer("Выберите игру для добавления:", reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith("select_new_game_"))
async def select_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    game = callback.data.split("_")[-1]

    await state.update_data(
            games={},
            game=game,
            game_rank="",
            process="adding_new_game"
    )

    await edit_game_rank(callback, state)
        
@router.callback_query(F.data.startswith("update_game_"))
async def get_game(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    game = callback.data.split("_")[-1]
    await callback.message.answer(f"Выберите, что вы хотите изменить в {game}", reply_markup=await get_read_game_kb(game))

@router.callback_query(F.data.startswith("edit_rank_"))
async def edit_game_rank_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    game = callback.data.split("_")[-1]
    data = await state.get_data()

    if "process" in data and data["process"] == "creating_profile":
        pass
    else:
        await state.update_data(
                games={},
                game=game,
                game_rank="",
                process="editing_rank"
        )

    await edit_game_rank(callback, state)


async def edit_game_rank(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    game = data["game"]

    if game in GAMES_RANKS:
        await callback.message.answer(text=TEXT_RANK.format(game=game), reply_markup=await get_ranks_kb(game))
        await state.set_state(EditProfileForm.rank)
    elif game == "Warcraft":
        await callback.message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb())
        await state.set_state(EditProfileForm.add_warcraft_mode)
    else:
        if game == "Raid Shadow Legends":
            await callback.message.answer(text=TEXT_RSL, reply_markup=ReplyKeyboardRemove())
        else:
            await callback.message.answer(text=TEXT_NUM_RANK, reply_markup=ReplyKeyboardRemove())
        await state.set_state(EditProfileForm.num_rank)

@router.message(EditProfileForm.num_rank)
async def save_num_rank(message: Message, state: FSMContext):
    data = await state.get_data()
    game = data["game"]

    if message.text:
        try:
            float(message.text)
        except Exception as e:
            print(e)
            await message.answer("Напиши число.")
            return
        
        if "process" in data:
            if data["process"] in ("editing_rank", "creating_profile"):
                await repository.update_game_rank(user_id=message.from_user.id, game=game, rank=message.text)
                if data["process"] == "creating_profile":
                    await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                    await message.answer("Вернуться к проверке анкеты?", 
                                                        reply_markup=await get_back_to_check_kb())
                    await state.set_state(EditProfileForm.clear)
                                
                else:
                    await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                    await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                    await state.clear()

            elif data["process"] == "adding_new_game":
                await state.update_data(
                game_rank=message.text
                            )
                await message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(False))
                await state.set_state(EditProfileForm.gallery)
        else:
            await message.answer("Произошла какая-то ошибка...")
    else:
        await message.answer("Напиши число.")

@router.callback_query(EditProfileForm.add_warcraft_mode)
async def save_mode(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = callback.data.split("_")[-1]
    if text:
        if text in WARCRAFT_MODES + ["skip"]:
            data = await state.get_data()
            rank = data["game_rank"]
            game = data["game"]

            if text not in rank:

                if text == "skip":
                    if rank:
                        rank += ""
                    else:
                        rank = "" 

                    
                    if "process" in data:
                        if data["process"] in ("editing_rank", "creating_profile"):
                            await repository.update_game_rank(user_id=callback.from_user.id, game=game, rank=rank)
                            if data["process"] == "creating_profile":
                                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                                await callback.message.answer("Вернуться к проверке анкеты?", 
                                                        reply_markup=await get_back_to_check_kb())
                                await state.set_state(EditProfileForm.clear)
                                
                            else:
                                await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                                await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                                await state.clear()

                        elif data["process"] == "adding_new_game":
                            await state.update_data(
                            game_rank=rank
                            )
                            await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(False))
                            await state.set_state(EditProfileForm.gallery)
                    else:
                        await callback.message.answer("Произошла какая-то ошибка...")
                else:
                    mode = text
                    await state.update_data(mode=mode)
                    is_pve = mode == "PvE"

                    await callback.message.answer(text="Выбери рейтинг из списка:", reply_markup=await get_warcraft_ranks_kb(is_pve=is_pve))
                    await state.set_state(EditProfileForm.add_warcraft_rank)
            else:
                await callback.message.answer("Вы уже выбрали этот режим. Выберите другой.")

        else:
            await callback.message.answer("Выберите режим из предложенного списка.")
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR)

@router.callback_query(EditProfileForm.add_warcraft_rank)
async def save_warcraft_rank(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "back_from_warcraft_ranks":
        await callback.message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb())
        await state.set_state(EditProfileForm.add_warcraft_mode)
        return
    elif callback.data.startswith("ranks_page_"):
        await handle_ranks_pagination(callback, state)
        return
    
    # Parse the callback data to get index and is_pve flag
    parts = callback.data.split("/")
    if len(parts) >= 3 and parts[0] == "add_warcraft_rank":
        try:
            rank_index = int(parts[1])
            is_pve_str = parts[2]
            is_pve = is_pve_str.lower() == 'true'
            # Get the actual rank based on the stored state or recreate the list
            ranks = WARCRAFT_PvE if is_pve else WARCRAFT
            if 0 <= rank_index < len(ranks):
                rank = ranks[rank_index]
                await callback.message.edit_text(f"Выбран рейтинг: {rank}", reply_markup=None)
            else:
                await callback.message.answer("Произошла какая-то ошибка... Попытайтесь позже")
                return
        except (ValueError, IndexError) as e:
            await callback.message.answer("Произошла какая-то ошибка... Попытайтесь позже")
            print(e)
            return
    else:
        await callback.message.answer("Произошла какая-то ошибка... Попытайтесь позже")
        return
    
    data = await state.get_data()
    games = data["games"]
    game = data["game"]
    game_rank = data["game_rank"]
    mode = data["mode"]

    new_rank = (game_rank + f"{mode}/{rank};")


    await state.update_data(
            games=games,
            game=game,
            mode=None,
            game_rank=new_rank
        )
    
    await callback.message.answer("Выбери режим из списка, в котором хочешь указать рейтинг:", reply_markup=await get_warcraft_modes_kb())
    await state.set_state(EditProfileForm.add_warcraft_mode)


async def handle_ranks_pagination(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    page = int(callback.data.split("_")[-1])
    mode = callback.data.split("_")[-2]
    data = await state.get_data()
    
    await state.update_data(current_page=page)
    keyboard = await get_warcraft_ranks_kb(is_pve=True, page=page) if mode == "pve" else await get_warcraft_ranks_kb(is_pve=False, page=page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(EditProfileForm.rank)
async def save_rank(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = callback.data.split("_")[-1]

    data = await state.get_data()
    game = data["game"]
    
    if text:
        if text == "Пропустить":
            rank = None
        else:
            rank = text
            if game in ["Raid Shadow Legends", "WoR"]:
                try:
                    float(rank)
                except Exception:
                    await callback.message.answer("Введите численное значение!")
                    return 

            

        if "process" in data:
            if data["process"] in ("editing_rank", "creating_profile"):
                await repository.update_game_rank(user_id=callback.from_user.id, game=game, rank=rank)
                if data["process"] == "creating_profile":
                    await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                    await callback.message.answer("Вернуться к проверке анкеты?", 
                                                        reply_markup=await get_back_to_check_kb())
                    await state.set_state(EditProfileForm.clear)
                    
                else:
                    await callback.message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                    await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                    await state.clear()

            elif data["process"] == "adding_new_game":
                await state.update_data(
                game_rank=rank
                )
                await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(False))
                await state.set_state(EditProfileForm.gallery)
        else:
            await callback.message.answer("Произошла какая-то ошибка...")
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(EditProfileForm.rank)

@router.callback_query(F.data.startswith("edit_gallery_"))
async def edit_game_gallery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    game = callback.data.split("_")[-1]
    data = await state.get_data()

    if "process" in data and data["process"] == "creating_profile":
        pass
    else:
        await state.update_data(
                games={},
                game=game,
                process="editing_gallery"
        )
    await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(False))
    await state.set_state(EditProfileForm.gallery)

@router.message(EditProfileForm.gallery)
async def save_gallery(message: Message, state: FSMContext, album: list[Message] = None):
    data = await state.get_data()
    game = data["game"]
    rank = data.get("game_rank", "")
    
    if message.photo:

        if album:

            if len(album) <= 10:

                if "process" in data:
                    if data["process"] in ("editing_gallery", "creating_profile"):
                        await repository.update_game_gallery(user_id=message.from_user.id, game=game, gallery=[photo.photo[-1].file_id for photo in album])
                        if data["process"] == "creating_profile":
                            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                            await message.answer("Вернуться к проверке анкеты?", 
                                                                reply_markup=await get_back_to_check_kb())
                            await state.set_state(EditProfileForm.clear)
                            
                        else:
                            await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                            await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                            await state.clear()

                    elif data["process"] == "adding_new_game":
                        await repository.create_game(
                            user_id=message.from_user.id,
                            name=game,
                            rank=rank,
                            gallery=[photo.photo[-1].file_id for photo in album]
                        )
                        await message.answer(f"Игра {game} успешно добавлена!", reply_markup=await get_back_to_menu())
                        await state.clear()
        else:
            if "process" in data:
                if data["process"] in ("editing_gallery", "creating_profile"):
                    await repository.update_game_gallery(user_id=message.from_user.id, game=game, gallery=[message.photo[-1].file_id])
                    if data["process"] == "creating_profile":
                        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                        await message.answer("Вернуться к проверке анкеты?", 
                                                                reply_markup=await get_back_to_check_kb())
                        await state.set_state(EditProfileForm.clear)
                        
                    else:
                        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                        await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                        await state.clear()

                elif data["process"] == "adding_new_game":
                    await repository.create_game(
                            user_id=message.from_user.id,
                            name=game,
                            rank=rank,
                            gallery=[message.photo[-1].file_id]
                        )
                    await message.answer(f"Игра {game} успешно добавлена!", reply_markup=await get_back_to_menu())
                    await state.clear()
                    
            else:
                await message.answer("Произошла какая-то ошибка...")
        
    elif message.text:
        if message.text == "Пропустить":

            if "process" in data:
                if data["process"] in ("editing_gallery", "creating_profile"):
                    await repository.update_game_gallery(user_id=message.from_user.id, game=game, gallery=None)
                    if data["process"] == "creating_profile":
                        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                        await message.answer("Вернуться к проверке анкеты?", 
                                                            reply_markup=await get_back_to_check_kb())
                        await state.set_state(EditProfileForm.clear)
                        
                    else:
                        await message.answer(TEXT_SUCCESS_EDIT, reply_markup=ReplyKeyboardRemove())
                        await message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
                        await state.clear()

                elif data["process"] == "adding_new_game":
                    await repository.create_game(
                        user_id=message.from_user.id,
                        name=game,
                        rank=rank,
                        gallery=None
                    )
                    await message.answer(f"Игра {game} успешно добавлена!", reply_markup=await get_back_to_menu())
                    await state.clear()
            else:
                await message.answer("Произошла какая-то ошибка...")
    else:
        await message.answer("Пришлите фотографии или выберите ответ с клавиатуры!")

@router.callback_query(F.data.startswith("delete_game_"))
async def edit_game_gallery(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    game = callback.data.split("_")[-1]
    await repository.delete_game(callback.from_user.id, game)

    await callback.message.answer(f"Игра {game} была удалена.", reply_markup=ReplyKeyboardRemove())
    await callback.message.answer(TEXT_BACK_TO_MENU, reply_markup=await get_back_to_menu())
    await state.clear()




@router.callback_query(F.data == "back_to_profile_check")
async def back_to_profile_check(callback: CallbackQuery, state: FSMContext):
    """Возврат к проверке анкеты после редактирования"""
    from .create_profile import check_profile
    
    await state.set_state(ProfileForm.check_profile)
    await check_profile(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "get_back_from_games_to_creating_profile")
async def get_back_from_games_to_creating_profile(callback: CallbackQuery, state: FSMContext):
     await callback.answer()
     await callback.message.delete()
     await callback.message.answer("Вернуться к проверке анкеты?", 
                                                            reply_markup=await get_back_to_check_kb())