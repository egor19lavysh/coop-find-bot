from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from states.create_profile import *
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository
from handlers.menu import cmd_menu
from .edit_profile import start_edit_profile_message



router = Router()


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
TEXT_ALLOW_INVITATIONS = "Разрешить присылать приглашения в игру от других пользователей? При отклонении ты сможешь отправлять сообщения самостоятельно. "
TEXT_SKIP = '\n\n<i>Если не хочешь заполнять эту информацию, напиши в чат "Пропустить"</i>'
TEXT_ANSWER_TYPE_ERROR = "Ответь текстом."
TEXT_WRONG_ANSWER = "Выберите ответ из предложенного списка!"
TEXT_PHOTO_ERROR = 'Пришлите фотографию профиля или выберите доступный вариант ответа ("Фото с профиля" или "Пропустить")'
TEXT_PHOTO_COUNT_ERROR = "Пришлите 1 фотографию"
TEXT_REPEAT_PROFILE = "Заполни заново свою анкету"
TEXT_ACCEPTED = "\n\nПодтвеждено ✅"
TEXT_REJECTED = "\n\nОтклонено ❌"
TEXT_ALREADY_HAVE_PROFILE = "У тебя уже есть анкета.\nТы можешь ее удалить или изменить"
IS_PROFILE_OK = "Все верно?"
TEXT_ADD_GAME = "Добавить еще игру?"
TEXT_BACK = "Назад"
TEXT_WARCRAFT_MODE = "Выбери режим из списка, в котором хочешь указать рейтинг:"
TEXT_NUM_RANK = "Введи силу аккаунта числом:"
TEXT_GALLERY = "Отправь скриншоты игрового профиля, до 10 шт. (по желанию)"
TEXT_TIME = "Выбери, пожалуйста, удобное время для игры по МСК:"

# В хендлерах замените вызовы клавиатур на:

@router.callback_query(F.data == "create_profile")
async def start_profile_with_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id
    )
    await callback.answer()

    await start_profile(bot=callback.bot, state=state)

async def start_profile(bot: Bot, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    chat_id = data["chat_id"]

    if not await repository.get_profile(user_id=user_id):
        await bot.send_message(chat_id=chat_id, text=TEXT_NICK, reply_markup=await get_back_kb())
        await state.update_data(
            games={},
            game=None,
            game_rank="",
            goals=[],
            process="creating_profile",
            time=[]
        )
        await state.set_state(ProfileForm.nickname)
    else:
        await bot.send_message(chat_id=chat_id, text=TEXT_ALREADY_HAVE_PROFILE)

@router.message(ProfileForm.nickname)
async def save_nickname(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer("Создание анкеты отменено.", reply_markup=await get_back_to_menu())
        await state.clear()
        return
    
    if message.text:
        await state.update_data(nickname=message.text)
        await message.answer(text=TEXT_TAG, reply_markup=await get_tag_kb())
        await state.set_state(ProfileForm.telegram_tag)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_back_kb())
        await state.set_state(ProfileForm.nickname)

@router.message(ProfileForm.telegram_tag)
async def save_telegram_tag(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_NICK, reply_markup=await get_back_kb())
        await state.set_state(ProfileForm.nickname)
        return
    
    if message.text:
        if message.text == "Пропустить":
            await state.update_data(telegram_tag=None)
        elif message.text == "Отправить данные":
            await state.update_data(telegram_tag=message.from_user.username)
        else:
            await state.update_data(telegram_tag=message.text)
        
        await message.answer(text=TEXT_GENDER, reply_markup=await get_gender_keyboard(with_back=True))
        await state.set_state(ProfileForm.gender)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_tag_kb())
        await state.set_state(ProfileForm.telegram_tag)

@router.message(ProfileForm.gender)
async def save_gender(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_TAG, reply_markup=await get_tag_kb())
        await state.set_state(ProfileForm.telegram_tag)
        return
    
    if message.text:
        if message.text == "Пропустить":
            await state.update_data(gender=None)
        else:
            if message.text in GENDER_LIST:
                await state.update_data(gender=message.text)
            else:
                await message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_gender_keyboard())
                await state.set_state(ProfileForm.gender)
                return
        
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ProfileForm.game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_gender_keyboard())
        await state.set_state(ProfileForm.gender)

@router.callback_query(ProfileForm.game)
async def save_game(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back_from_games":
        await callback.message.answer(text=TEXT_GENDER, reply_markup=await get_gender_keyboard())
        await state.set_state(ProfileForm.gender)
        await callback.answer()
        return
    
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
                await callback.message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(ProfileForm.add_new_game)
                return
        else:
            await callback.message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_game_kb(with_back=True))
            await state.set_state(ProfileForm.game)
            return
        
        if game in GAMES_RANKS:
            await callback.message.answer(text=TEXT_RANK.format(game=game), reply_markup=await get_ranks_kb(game, with_back=True))
            await state.set_state(ProfileForm.rank)
        elif game == "Warcraft":
            await callback.message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb(True))
            await state.set_state(ProfileForm.add_warcraft_mode)
        else:
            await callback.message.answer(text=TEXT_NUM_RANK, reply_markup=ReplyKeyboardRemove())
            await state.set_state(ProfileForm.rank)
    else:
        await callback.message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ProfileForm.game)

@router.message(ProfileForm.add_warcraft_mode)
async def save_mode(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ProfileForm.game)
        return
    
    if message.text:
        if message.text in WARCRAFT_MODES + ["Пропустить"]:
            data = await state.get_data()
            rank = data["game_rank"]

            if message.text not in rank:

                if message.text == "Пропустить":
                    if rank:
                        rank += ""
                    else:
                        rank = "" 

                    await state.update_data(
                        game_rank=rank
                    )

                    await message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(with_back=True))
                    await state.set_state(ProfileForm.gallery)

                else:
                    mode = message.text
                    await state.update_data(mode=mode)
                    is_pve = mode == "PvE"

                    await message.answer(text="Выбери рейтинг из списка:", reply_markup=await get_warcraft_ranks_kb(is_pve=is_pve))
                    await state.set_state(ProfileForm.add_warcraft_rank)
            else:
                await message.answer("Вы уже выбрали этот режим. Выберите другой.")

        else:
            await message.answer("Выберите режим из предложенного списка.")
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)

@router.callback_query(ProfileForm.add_warcraft_rank)
async def save_warcraft_rank(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "back_from_warcraft_ranks":
        await callback.message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb(True))
        await state.set_state(ProfileForm.add_warcraft_mode)
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
    
    await callback.message.answer("Выбери режим из списка, в котором хочешь указать рейтинг:", reply_markup=await get_warcraft_modes_kb(True))
    await state.set_state(ProfileForm.add_warcraft_mode)


async def handle_ranks_pagination(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    page = int(callback.data.split("_")[-1])
    mode = callback.data.split("_")[-2]
    data = await state.get_data()
    
    await state.update_data(current_page=page)
    keyboard = await get_warcraft_ranks_kb(is_pve=True, page=page) if mode == "pve" else await get_warcraft_ranks_kb(is_pve=False, page=page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()

@router.message(ProfileForm.add_new_warcraft_rank)
async def add_new_warcraft_rank(message: Message, state: FSMContext):
    if message.text:
        if message.text == "Да":
            await message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb(True))
            await state.set_state(ProfileForm.add_warcraft_mode)
        elif message.text == "Нет":
            await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_game)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb(False))
            await state.set_state(ProfileForm.add_new_warcraft_rank)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb(False))
        await state.set_state(ProfileForm.add_new_warcraft_rank)


@router.message(ProfileForm.rank)
async def save_rank(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ProfileForm.game)
        return
    
    data = await state.get_data()
    game = data["game"]
    
    if message.text:
        if message.text == "Пропустить":
            rank = None
        else:
            rank = message.text
            if game in ["Raid Shadow Legends", "WoR"]:
                try:
                    float(rank)
                except Exception:
                    await message.answer("Введите численное значение!")
                    return 

            

        await state.update_data(
            game_rank=rank
        )
        
        await message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(ProfileForm.gallery)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(ProfileForm.rank)

@router.message(ProfileForm.gallery)
async def save_gallery(message: Message, state: FSMContext, album: list[Message] = None):
    data = await state.get_data()
    games = data["games"]
    game = data["game"]
    rank = data["game_rank"]
    
    if message.media_group_id and message.photo:

        if len(album) <= 10:

            games[game] = {
                "rank": rank,
                "gallery": [photo.photo[-1].file_id for photo in album]
            }

            await state.update_data(
                games=games,
                game=game,
                game_rank=rank
            )
        
            await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_game)
        else:
            await message.answer("Отправьте до 10 фотографий.")
            return
        
    elif message.text:
        if message.text == "Пропустить":

            games[game] = {
                "rank": rank,
                "gallery": []
            }

            await state.update_data(
                games=games,
                game=game,
                game_rank=rank
            )
        
            await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_game)

        elif message.text == "Назад":
            if game in GAMES_RANKS:
                await message.answer(text=TEXT_RANK.format(game=game), reply_markup=await get_ranks_kb(game, with_back=True))
                await state.set_state(ProfileForm.rank)
            elif game == "Warcraft":
                await message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb(True))
                await state.set_state(ProfileForm.add_warcraft_mode)
            else:
                await message.answer(text=TEXT_NUM_RANK, reply_markup=ReplyKeyboardRemove())
                await state.set_state(ProfileForm.rank)
        else:
            await message.answer("Пришлите фотографии или выберите ответ с клавиатуры!")

        

@router.message(ProfileForm.add_new_game)
async def add_new_game(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        data = await state.get_data()
        games = data["games"]
        
        # if games:
        #     # Удаляем последнюю добавленную игру
        #     last_game = list(games.keys())[-1]
        #     del games[last_game]
        #     await state.update_data(games=games)
            
        #     if games:  # Если остались игры, возвращаемся к выбору добавления
        #         await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
        #         await state.set_state(ProfileForm.add_new_game)
        #     else:  # Если игр не осталось, возвращаемся к выбору первой игры
        #         await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        #         await state.set_state(ProfileForm.game)
        await message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(ProfileForm.gallery)
        return
    
    if message.text:
        if message.text == "Да":
            await message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
            await state.set_state(ProfileForm.game)
        elif message.text == "Нет":
            await message.answer(text=TEXT_TIME, reply_markup=await get_time_kb(True))
            await state.set_state(ProfileForm.time)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_game)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.add_new_game)

@router.message(ProfileForm.time)
async def save_time(message: Message, state: FSMContext):
    data = await state.get_data()
    time = data["time"]

    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_ADD_GAME, reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.add_new_game)
        return
    
    if message.text:
        if message.text in CONVENIENT_TIME:
            if message.text not in time:
                time.append(message.text)
                await state.update_data(time=time)
                await message.answer(text="Добавить еще промежуток время?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(ProfileForm.add_new_time)
            else:
                await message.answer("Вы уже выбрали этот промежуток времени. Теперь выберите другой:", reply_markup=await get_time_kb(with_back=True))
        else:
            await message.answer(text="Выбери промежуток времени из списка.")
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_time_kb(with_back=True))

@router.message(ProfileForm.add_new_time)
async def add_new_time(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        data = await state.get_data()
        time = data["time"]
        
        if time:
            time.pop()
            await state.update_data(time=time)
            
            if time:  # Если остались игры, возвращаемся к выбору добавления
                await message.answer(text="Добавить еще промежуток времени?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(ProfileForm.add_new_time)
            else:  # Если игр не осталось, возвращаемся к выбору первой игры
                await message.answer(text=TEXT_TIME, reply_markup=await get_time_kb(with_back=True))
                await state.set_state(ProfileForm.time)
        return
    
    if message.text:
        if message.text == "Да":
            await message.answer(text=TEXT_TIME, reply_markup=await get_time_kb(with_back=True))
            await state.set_state(ProfileForm.time)
        elif message.text == "Нет":
            await message.answer(text=TEXT_ABOUT, reply_markup=await get_back_kb())
            await state.set_state(ProfileForm.about)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_time)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.add_new_time)

@router.message(ProfileForm.about)
async def save_about(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        await message.answer(text="Добавить еще промежуток времени?", reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.add_new_time)
        return
    
    if message.text:
        await state.update_data(about=message.text)
        await message.answer(text=TEXT_GOAL, reply_markup=await get_goals_kb(with_back=True))
        await state.set_state(ProfileForm.goal)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_back_kb())
        await state.set_state(ProfileForm.about)

@router.message(ProfileForm.goal)
async def save_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    goals = data["goals"]

    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_ABOUT, reply_markup=await get_back_kb())
        await state.update_data(goals=[])
        await state.set_state(ProfileForm.about)
        return
    
    if message.text:
        if message.text in GOALS_LIST:
            if message.text not in goals:
                goals.append(message.text)
                await state.update_data(goals=goals)
                await message.answer(text="Добавить еще цель?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(ProfileForm.add_new_goal)
            else:
                await message.answer("Вы уже выбрали эту цель. Теперь выберите другую:", reply_markup=await get_goals_kb(with_back=True))
        else:
            await message.answer(text="Выбери цель из списка.")
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_goals_kb(with_back=True))

@router.message(ProfileForm.add_new_goal)
async def add_new_goal(message: Message, state: FSMContext):
    if message.text == TEXT_BACK:
        data = await state.get_data()
        goals = data["goals"]
        
        if goals:
            goals.pop()
            await state.update_data(goals=goals)
            
            if goals:
                await message.answer(text="Добавить еще цель?", reply_markup=await get_confirmation_kb(with_back=True))
                await state.set_state(ProfileForm.add_new_goal)
            else:
                await message.answer(text=TEXT_GOAL, reply_markup=await get_goals_kb(with_back=True))
                await state.set_state(ProfileForm.goal)
        return
    
    if message.text:
        if message.text == "Да":
            await message.answer(text=TEXT_GOAL, reply_markup=await get_goals_kb(with_back=True))
            await state.set_state(ProfileForm.goal)
        elif message.text == "Нет":
            await message.answer(text=TEXT_PHOTO, reply_markup=await get_photo_kb(with_back=True))
            await state.set_state(ProfileForm.photo)
        else:
            await message.answer(text=TEXT_WRONG_ANSWER, reply_markup=await get_confirmation_kb(with_back=True))
            await state.set_state(ProfileForm.add_new_goal)
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR, reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.add_new_goal)
    

@router.message(ProfileForm.photo)
async def save_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_BACK:
        await message.answer(text=TEXT_GOAL, reply_markup=await get_goals_kb(with_back=True))
        await state.set_state(ProfileForm.goal)
        return
    
    # Проверяем, что это текст, а не несколько фото
    if message.text:
        if message.text == "Фото с профиля":
            photos = await message.bot.get_user_profile_photos(message.from_user.id)
    
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
                file_id = photo.file_id
            else:
                file_id = None

            await state.update_data(photo=file_id)

        elif message.text == "Пропустить":
            await state.update_data(photo=None)
        else:
            await message.answer(TEXT_PHOTO_ERROR, reply_markup=await get_photo_kb(with_back=True))
            return  # убрал повторную установку состояния

    # Обработка фото - проверяем количество
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
        file_id = message.photo[-1].file_id
        await state.update_data(photo=file_id)
            
    
    # Если пришел неподдерживаемый тип контента
    else:
        await message.answer(TEXT_PHOTO_ERROR, reply_markup=await get_photo_kb(with_back=True))
        return  # убрал повторную установку состояния

    await check_profile(message=message, state=state)

async def check_profile(message: Message, state: FSMContext):
    data = await state.get_data()

    nickname = data["nickname"]
    telegram_tag = data["telegram_tag"] if data["telegram_tag"] else "Нет"
    gender = data["gender"] if data["gender"] else "Нет"
    games = data["games"]
    about = data["about"]
    goals = data["goals"]
    photo = data["photo"]
    time = data["time"]


    games_str = ", ".join(games)
    time_str = ", ".join(time)
    goals_str = ", ".join(goals)

    profile = PROFILE_SAMPLE.format(
                    nickname=nickname,
                    telegram_tag=telegram_tag,
                    gender=gender,
                    game=games_str,
                    about=about,
                    time=time_str,
                    goal=goals_str
                )

    if photo:
        try:
            await message.answer_photo(
                photo=photo,
                caption=profile
            )
        except:
            await message.answer(
                text=profile + PHOTO_SAMPLE
            )
    else:
        await message.answer(
                text=profile + PHOTO_SAMPLE
            )
        
    await message.answer(text=IS_PROFILE_OK, reply_markup=await get_commit_profile_kb(with_back=False))
    await state.set_state(ProfileForm.check_profile)


@router.callback_query(ProfileForm.check_profile, F.data.in_(["profile_correct", "profile_incorrect", "back_from_check"]))
async def commit_profile(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    if callback.data == "back_from_check":
        await callback.message.answer(text=TEXT_PHOTO, reply_markup=await get_photo_kb(with_back=True))
        await state.set_state(ProfileForm.photo)
        await callback.answer()
        return
    
    if not await repository.get_profile(user_id=callback.from_user.id):
        await save_profile(callback=callback, state=state)
    
    if callback.data == "profile_correct":
        await callback.message.answer(text=TEXT_SUCCESS, reply_markup=ReplyKeyboardRemove())
        await state.set_state(ProfileForm.is_active)
        await callback.message.answer(text=TEXT_ALLOW_INVITATIONS, reply_markup=await get_status_kb(with_back=True))
        await callback.answer()
    
    elif callback.data == "profile_incorrect":
        await callback.message.answer(text="Редактируем анкету...")
        await start_edit_profile_message(callback.message, state)
        # Состояние изменится в процессе редактирования, поэтому не меняем его здесь
        await callback.answer()

@router.callback_query(ProfileForm.is_active)
async def save_status(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back_from_status":
        await callback.message.answer(text=IS_PROFILE_OK, reply_markup=await get_commit_profile_kb(with_back=True))
        await state.set_state(ProfileForm.check_profile)
        await callback.answer()
        return
    
    
    
    status = callback.data.split("_")[-1]
    if status == "true":
        await repository.activate_profile(user_id=callback.from_user.id)
    elif status == "false":
        await repository.deactivate_profile(user_id=callback.from_user.id)
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
    
    await state.clear()

    await cmd_menu(callback.message)


async def save_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await repository.create_profile(
        user_id = data["user_id"] if "user_id" in data else callback.from_user.id,
        nickname = data["nickname"],
        games = data["games"],
        time=data["time"],
        about = data["about"],
        goals = data["goals"],
        is_active = data.get("is_activate", False),
        telegram_tag = data["telegram_tag"],
        gender = data["gender"],
        photo = data["photo"]
    )