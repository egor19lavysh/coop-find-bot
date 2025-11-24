from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from utils.constants import *
from utils.schedule_estimate import schedule_estimate
from keyboards.search_kb import *
from repositories.profile_repository import profile_repository as repository
from repositories.clan_repository import clan_repository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from utils.level_up import level_up
from states.search import *
from utils.ranks import *
from keyboards.profile_kb import get_ranks_kb, get_warcraft_modes_kb, get_warcraft_ranks_kb
from .profile.create_profile import TEXT_WARCRAFT_MODE, handle_ranks_pagination


router = Router()

### НОВЫЕ ТЕКСТЫ
TEXT_CHOOSE_SEARCH_TYPE = """Выбери, кого хочешь найти:
🗡️ Анкеты игроков — если ищешь одного игрока.
🛡️ Кланы — если хочешь найти сообщество игроков.
"""
TEXT_CHOOSE_GAME = "Выбери игру для поиска"
TEXT_NO_CLANS = "Активных кланов по {game} не нашлось..."
TEXT_CLANS_FOUND = "Найденные кланы:"
TEXT_JOIN_CLAN = "Отправить заявку на вступление в клан"
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

@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(GameForm.search_type)
    await message.answer(
        text=TEXT_CHOOSE_SEARCH_TYPE, 
        reply_markup=await get_search_type_kb()
    )

@router.callback_query(F.data == "start_search")
async def start_search_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(GameForm.search_type)
    await callback.message.answer(
        text=TEXT_CHOOSE_SEARCH_TYPE, 
        reply_markup=await get_search_type_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("search_type_"))
async def choose_search_type(callback: CallbackQuery, state: FSMContext):
    search_type = callback.data.split("_")[-1]
    await callback.answer()

    await callback.message.delete()
    
    await state.update_data(search_type=search_type)
    if search_type != "profiles":
        await state.set_state(GameForm.game)
        
        await callback.message.answer(
            text=TEXT_CHOOSE_GAME,
            reply_markup=await get_game_inline_kb()
        )
    else:
        await callback.message.answer("Выберите вид поиска:", reply_markup=await get_search_profiles_types())

@router.callback_query(F.data == "game_search")
async def game_search(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.delete()
    
    await state.set_state(GameForm.game)
        
    await callback.message.answer(
            text=TEXT_CHOOSE_GAME,
            reply_markup=await get_game_inline_kb()
        )

@router.callback_query(F.data.startswith("get_profiles_by_"))
async def get_profiles_callback_handler(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    game = callback.data.split("_")[-1]
    data = await state.get_data()
    search_type = data.get("search_type", "profiles")
    
    await callback.answer()
    
    if search_type == "profiles":
        await get_profiles_by_game_callback(callback, state, game)
    elif search_type == "clans":
        await get_clans_by_game_callback(callback, state, game)

async def get_profiles_by_game_callback(callback: CallbackQuery, state: FSMContext, game: str):
    profiles = await repository.get_profiles_by_game(game=game, user_id=callback.from_user.id)
    #await callback.message.delete()
    
    if profiles:
        await state.clear()
        await state.update_data(profiles=profiles, current_page=0, game=game, search_type="profiles")
        
        keyboard = await get_profiles_kb(profiles, game=game, page=0)
        await callback.message.edit_text(
            text=TEXT_PROFILES_FOUND,
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=TEXT_NO_PROFILES.format(game=game))
        await callback.message.edit_reply_markup(reply_markup=await get_back_to_games_kb("profiles"))
        await state.clear()

async def get_clans_by_game_callback(callback: CallbackQuery, state: FSMContext, game: str):
    clans = await clan_repository.get_clans_by_game(game=game, user_id=callback.from_user.id)
    #await callback.message.delete()
    
    if clans:
        await state.clear()
        await state.update_data(clans=clans, current_page=0, game=game, search_type="clans")
        
        keyboard = await get_clans_kb(clans, page=0)
        await callback.message.edit_text(
            text=TEXT_CLANS_FOUND
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=TEXT_NO_CLANS.format(game=game))
        await callback.message.edit_reply_markup(reply_markup=await get_back_to_games_kb("clans"))
        await state.clear()

# Хендлеры для профилей
@router.callback_query(F.data.startswith("profiles_page_"))
async def handle_profiles_pagination(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    profiles = data.get("profiles", [])
    game = data["game"]
    
    if profiles:
        await state.update_data(current_page=page)
        keyboard = await get_profiles_kb(profiles, game=game, page=page)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data.startswith("send_message_to_user_"))
async def send_message(callback: CallbackQuery, state: FSMContext):

    user_id = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    game = data.get("game")
    
    await state.set_state(SendMessageForm.message)
    await state.update_data(
        user_id=user_id,
        game=game
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
        

        postfix = ""
        if message.from_user.username:
            postfix = TEXT_ADDITIONAL_INFO.format(tag="@" + message.from_user.username)
                
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=TEXT_MESSAGE.format(name=message.from_user.full_name, message=message.text) + postfix,
                reply_markup=await get_to_dialog_with_user_kb(username=message.from_user.username) if message.from_user.username else None
            )
            await message.answer(text=TEXT_SENT_MESSAGE, reply_markup=await get_back_kb())

            if profile := await repository.get_profile(user_id=message.from_user.id):
                if not profile.send_first_message:
                    new_xp = profile.experience + 20
                    if profile.experience // 100 < new_xp // 100:
                        await level_up(message.bot, profile.user_id, new_xp // 100 + 1)
                    await repository.add_experience(user_id=profile.user_id, experience=20)
                    await repository.update_send_first_message(user_id=profile.user_id)
                

        except:
            await message.answer(text=TEXT_TRIED_TO_SEND_MESSAGE, reply_markup=await get_back_kb())
        
        # Очищаем состояние, но сохраняем игру для возможности вернуться
        await state.clear()
        await state.update_data(game=game, search_type="profiles")
    else:
        await message.answer(text=TEXT_ANSWER_TYPE_ERROR)
        await state.set_state(SendMessageForm.message)

@router.callback_query(F.data.startswith("invite_user_"))
async def invite_user(callback: CallbackQuery, state: FSMContext, apscheduler: AsyncIOScheduler):

    callback_parts = callback.data.split("_")
    teammate_id = int(callback_parts[-1])
    game = callback_parts[-2]
    profile = await repository.get_profile(user_id=teammate_id)
    user_profile = await repository.get_profile(user_id=callback.from_user.id)

    if not profile:
        await callback.answer("Профиль не найден")
        return

    postfix = ""
    if callback.from_user.username:
        postfix = TEXT_ADDITIONAL_INFO.format(tag="@" + callback.from_user.username)
    
    await state.update_data(game=game, search_type="profiles")
    
    try:
        keyboard = await get_invite_profile_kb(user_id=user_profile.user_id) if user_profile else None
        await callback.bot.send_message(
                chat_id=teammate_id,
                text=TEXT_INVITE.format(name=callback.from_user.full_name, game=game) + postfix,
                reply_markup=keyboard
            )
        await callback.message.answer(text=TEXT_SENT_MESSAGE, reply_markup=await get_back_kb())

        if callback.from_user.id not in profile.teammate_ids:
            dt = datetime.now() + timedelta(hours=24)
            await schedule_estimate(
                apscheduler=apscheduler,
                time=dt,
                bot=callback.bot,
                user_id=callback.from_user.id,
                teammate=profile.nickname,
                teammate_id=teammate_id,
                state=state
            )
    except Exception as e:
        await callback.message.answer(text=TEXT_TRIED_TO_SEND_MESSAGE, reply_markup=await get_back_kb())

    await callback.answer()

# Хендлеры для кланов
@router.callback_query(F.data.startswith("clans_page_"))
async def handle_clans_pagination(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    page = int(callback.data.split("_")[-1])
    data = await state.get_data()
    clans = data.get("clans", [])
    
    if clans:
        await state.update_data(current_page=page)
        keyboard = await get_clans_kb(clans, page=page)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data.startswith("view_clan_"))
async def view_clan_detail(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    clan_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    clans = data.get("clans", [])
    game = data.get("game")
    
    clan = next((c for c in clans if c.id == clan_id), None)
    
    if not clan:
        await callback.answer("Клан не найден")
        return

    
    clan_info = f"<b>Название клана</b>: {clan.name}\n\n"
    clan_info += f"<b>Игра</b>: {clan.game}\n\n"
    clan_info += f"<b>Описание</b>: {clan.description}\n\n"
    clan_info += f"<b>Требования</b>: {clan.demands}\n\n"

    if user := await callback.bot.get_chat(clan.user_id):
        if user.username:
            clan_info += f"<b>Тег лидера клана</b>: @{user.username}\n\n"

    if clan.created_at:
        time = clan.created_at.strftime('%d.%m.%Y %H:%M')
        clan_info += f"<b>Дата размещения</b>: {time}"
    
    
    await callback.answer()
    
    await callback.message.edit_text(
        text=clan_info,
        reply_markup=await get_clan_detail_kb(clan_id, game)
    )
    

@router.callback_query(F.data.startswith("join_clan_"))
async def join_clan(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    clan_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    clans = data.get("clans", [])
    
    
    clan = next((c for c in clans if c.id == clan_id), None)
    if not clan:
        await callback.answer("Клан не найден")
        return
    
    await state.update_data(game=clan.game)
    
    user_profile = await repository.get_profile(callback.from_user.id)
    username = user_profile.nickname if user_profile else callback.from_user.full_name
    
    join_message = f"🏰 Заявка на вступление в клан '{clan.name}'\n\n"
    join_message += f"👤 Игрок: {username}\n"
    join_message += f"🎮 Игра: {clan.game}\n"
    
    if user_profile:
        games = {game.name: game.rank for game in await repository.get_games_by_user_id(callback.from_user.id)}
        join_message += f"📊 Ранг: {games.get(clan.game, None) or 'Не указан'}\n"
        join_message += f"🎯 Цель: {user_profile.goal}\n"
    
    if callback.from_user.username:
        join_message += f"📞 Телеграм: @{callback.from_user.username}"
    
    join_message += "\n\nЧтобы принять пользователя, не стесняйся, напиши ему в личные сообщения"
    try:
        keyboard = await get_invite_profile_kb(user_id=user_profile.user_id, username=callback.from_user.username) if user_profile else None
        await callback.bot.send_message(
            chat_id=clan.user_id,
            text=join_message,
            reply_markup=keyboard
        )
        await callback.message.answer(TEXT_SENT_MESSAGE, reply_markup=await get_back_kb(search_type="clans"))

        new_xp = user_profile.experience + 30
        if user_profile.experience // 100 < new_xp // 100:
            await level_up(callback.bot, user_id=user_profile.user_id, new_level=new_xp // 100 + 1)
        await repository.add_experience(user_id=user_profile.user_id, experience=30)
        
    except Exception as e:
        await callback.message.answer(TEXT_TRIED_TO_SEND_MESSAGE, reply_markup=await get_back_kb(search_type="clans"))

    await callback.answer()

@router.callback_query(F.data.startswith("back_to_clans"))
async def back_to_clans(callback: CallbackQuery, state: FSMContext):
    # await callback.message.delete()

    data = await state.get_data()
    game = data.get("game")
    
    if game:
        clans = await clan_repository.get_clans_by_game(game=game, user_id=callback.from_user.id)
        
        if clans:
            await state.update_data(clans=clans, current_page=0)
            keyboard = await get_clans_kb(clans, page=0)
            await callback.message.edit_text(
                text=TEXT_CLANS_FOUND,
                reply_markup=keyboard
            )
    await callback.answer()

@router.callback_query(F.data == "close_clans_list")
async def close_clans_list(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "back_to_profiles")
async def get_back_to_profiles(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    data = await state.get_data()
    game = data.get("game")
    search_type = data.get("search_type", "profiles")
    
    if game:
        if search_type == "profiles":
            profiles = await repository.get_profiles_by_game(game=game, user_id=callback.from_user.id)
            if profiles:
                await state.update_data(profiles=profiles, current_page=0)
                keyboard = await get_profiles_kb(profiles, game=game, page=0)
                await callback.message.answer(
                    text=TEXT_PROFILES_FOUND,
                    reply_markup=keyboard
                )
        elif search_type == "clans":
            clans = await clan_repository.get_clans_by_game(game=game, user_id=callback.from_user.id)
            if clans:
                await state.update_data(clans=clans, current_page=0)
                keyboard = await get_clans_kb(clans, page=0)
                await callback.message.answer(
                    text=TEXT_CLANS_FOUND,
                    reply_markup=keyboard
                )
    await callback.answer()

@router.callback_query(F.data == "close_profiles_list")
async def close_profiles_list(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()

    await callback.message.delete()
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery):
    #await callback.message.delete()

    await callback.answer()

@router.callback_query(F.data == "filter_search")
async def filter_search(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Выберите игру:", reply_markup=await get_games_filter_search_kb())
    await state.set_state(SearchForm.game)

@router.callback_query(F.data.startswith("filter_game_"))
async def filter_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    game = callback.data.split("_")[-1]
    await state.update_data(game=game)

    if game in GAMES_RANKS:
        await callback.message.answer(f"Выберите ранг в {game}", reply_markup=await get_ranks_kb(game, True))
        await state.set_state(SearchForm.rank)
    elif game == "Warcraft":
        await callback.message.answer("Выберите режим:", reply_markup=await get_warcraft_modes_kb(True))
        await state.set_state(SearchForm.warcraft_mode)
    else:
        await callback.message.answer("Введите силу аккаунта числом:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(SearchForm.rank)


@router.message(SearchForm.rank)
async def save_rank(message: Message, state: FSMContext):
    data = await state.get_data()
    game = data["game"]

    if message.text:
        if message.text == "Назад":
            await message.answer("Выберите игру:", reply_markup=await get_games_filter_search_kb())
            await state.set_state(SearchForm.game)
            return 

        elif message.text == "Пропустить":
            await state.update_data(rank=None)

        elif message.text in GAMES_RANKS:
            await state.update_data(rank=message.text)
        elif game in ["Raid Shadow Legends", "WoR"]:
            try:
                float(message.text)
            except Exception:
                await message.answer("Введите численное значение!")
                return

            await state.update_data(
                rank=message.text
            )

        await message.answer("Выберите цель:", reply_markup=await get_goals_kb(True))
        await state.set_state(SearchForm.goal)

@router.message(SearchForm.warcraft_mode)
async def save_mode(message: Message, state: FSMContext):
    if message.text:
        if message.text in WARCRAFT_MODES:
            await state.update_data(
                mode=message.text
            )
            is_pve = message.text == "PvE"
            await message.answer("Выберите рейтинг:", reply_markup = await get_warcraft_ranks_kb(is_pve=is_pve))
            await state.set_state(SearchForm.warcraft_rank)
        elif message.text == "Пропустить":
            await state.update_data(
                rank=None
            )
            await message.answer("Выберите цель:", reply_markup=await get_goals_kb(True))
            await state.set_state(SearchForm.goal)
        elif message.text == "Назад":
            await message.answer("Выберите режим:", reply_markup=await get_warcraft_modes_kb(True))
            await state.set_state(SearchForm.warcraft_mode)
        else:
            await message.answer("Выберите ответ из списка!")
    else:
        await message.answer("Ответьте текстом!")


@router.callback_query(SearchForm.warcraft_rank)
async def save_warcraft_rank(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "back_from_warcraft_ranks":
        await callback.message.answer(text=TEXT_WARCRAFT_MODE, reply_markup=await get_warcraft_modes_kb(True))
        await state.set_state(SearchForm.warcraft_mode)
        return
    elif callback.data.startswith("ranks_page_"):
        await handle_ranks_pagination(callback, state)
        return

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
    
    await state.update_data(
        rank=data["mode"] + "/" + rank + ";"
    )

    await callback.message.answer("Выберите цель:", reply_markup=await get_goals_kb(True))
    await state.set_state(SearchForm.goal)




@router.message(SearchForm.goal)
async def save_goal(message: Message, state: FSMContext):
    data = await state.get_data()
    game = data["game"]

    if message.text:
        if message.text == "Назад":
            await message.answer(f"Выберите ранг в {game}", reply_markup=await get_ranks_kb(game, True))
            await state.set_state(SearchForm.rank)
            return

        elif message.text == "Пропустить":
            await state.update_data(goal=None)

        elif message.text in GOALS_LIST:
            await state.update_data(goal=message.text)

    await get_profiles_by_filter(message, state)


@router.callback_query(F.data == "profile_by_filters")
async def get_profiles_by_filter_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await get_profiles_by_filter(callback.message, state)

async def get_profiles_by_filter(message: Message, state: FSMContext):
    data = await state.get_data()
    game = data["game"]
    rank = data.get("rank", None)
    goal = data.get("goal",  None)
    profiles = await repository.get_profiles_by_filters(game=game, rank=rank, goal=goal, user_id=message.from_user.id)

    
    if profiles:
        await state.update_data(profiles=profiles, current_page=0, game=game, search_type="profiles")
        
        keyboard = await get_profiles_kb(profiles, game=game, page=0, need_filter=True)
        await message.answer(
            text=TEXT_PROFILES_FOUND,
            reply_markup=keyboard
        )
    else:
        await message.answer(text="Активных анкет по заданным фильтрам не нашлось...", reply_markup=await get_back_to_games_kb("profiles"))
        await state.clear()