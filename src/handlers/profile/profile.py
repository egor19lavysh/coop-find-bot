from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository
from .create_profile import start_profile
from statistic import Statistic
import asyncio


router = Router()

class PhotoForm(StatesGroup):
    photo = State()

### ТЕКСТЫ
TEXT_INTRO = "Отлично! Что ты хочешь изменить в своей анкете?"
TEXT_DELETE_PROFILE = "Твоя анкета удалена. Я не плачу, это просто пиксели."
TEXT_NO_PROFILE = "У тебя еще нет анкеты.\nСоздай ее командой /profile"
TEXT_SEND_PHOTO = "Пришли новое фото профиля в чат."
TEXT_PHOTO_UPDATED = "Фото профиля обновлено."
TEXT_PHOTO_ERROR = 'Пришлите фотографию профиля!'
TEXT_PROFILE_DEACTIVATED = "Твоя анкета снята с поиска. Ты сможешь ее разместить в любой момент."
TEXT_PROFILE_ACTIVATED = "Твоя анкета успешно размещена. Теперь ее видят другие пользователи."
TEXT_YOUR_CHOICE = "Анкета {name}"
TEXT_GALLERY = """
✨ Галерея игрока «{name}».
Тут находится результат его игры: его лут, сила аккаунта, персонажи, соборки и многое другое.

Если галерея не соответствует игре, отправь скрин в поддержку: @ggstore_support
"""
TEXT_CONFIRM_DELETE_PROFILE = """
Ты точно хочешь удалить анкету? Я буду грустить 🥺
"""


@router.message(Command("profile"))
async def update_profile(message: Message):
    await message.delete()
    await message.answer(text=TEXT_INTRO, reply_markup=(await get_profile_kb(user_id=message.from_user.id)).as_markup())

@router.callback_query(F.data == "profile")
async def update_profile_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=TEXT_INTRO, reply_markup=(await get_profile_kb(user_id=callback.from_user.id)).as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("read_profile"))
async def read_profile(callback: CallbackQuery, state: FSMContext, statistic: Statistic):
    asyncio.create_task(statistic.set_open_profile(callback.from_user.id))

    await callback.message.delete()

    callback_parts = callback.data.split("_")
    user_id = int(callback_parts[-1])
    if "filter" in callback_parts:
        type_user = "other"
    else:
        type_user = callback_parts[-2]


    if type_user == "other":
        data = await state.get_data()
        if "game" in data:
            game = data["game"]
        else:
            await callback.message.answer("Я потерял игру, по которой производится поиск. Попробуйте заново")
            await callback.answer()
            return 
    

    if profile := await repository.get_profile(user_id=user_id):

        games = {game.name: game.rank for game in profile.games}

        user_rank = None
        if type_user == "other":
            if games[game]:
                if game != "Warcraft":
                    user_rank = f"\n<b>Ранг:</b> {games[game]}"
                else:
                    user_rank = f"\n<b>Ранг:</b>\n"
                    subranks = []
                    for subrank in games[game].split(";")[:-1]:
                        mode, info = subrank.split("/")
                        subranks.append(f"- {mode}: {info}")
                    user_rank += "\n".join(subranks)
            else:
                user_rank = f"\n<b>Ранг:</b> Не указан"

        else:
            user_rank = ""

        if type_user == "other":
            keyboard = await get_interaction_kb(user_id=user_id, game=game) if "filter" not in callback.data else await get_interaction_kb(user_id=user_id, game=game, need_filter=True)
        elif type_user == "invite":
            user = await callback.bot.get_chat(user_id)
            keyboard = await get_back_to_main_menu_from_invite(user.username)
        else:
            keyboard = await get_back_to_menu()
            
        prefix = TEXT_YOUR_CHOICE.format(name=profile.nickname) if type_user == "other" else ""

        profile_text = prefix + FULL_PROFILE_SAMPLE.format(
            nickname=profile.nickname,
            telegram_tag= "@" + profile.telegram_tag if profile.telegram_tag else "Нет",
            gender=profile.gender if profile.gender else "Нет",
            level=profile.experience // 100 + 1,
            polite=str(round(profile.polite, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            skill=str(round(profile.skill, 1)) + "⭐" if profile.teammate_ids else "Нет оценок",
            team_game=str(round(profile.team_game, 1)) + "⭐" if profile.teammate_ids else "Нет оценок", 
            games=profile.games_str,
            rank=user_rank,
            add_info=PROFILE_ADD_INFO.format(time=", ".join(profile.convenient_time) if profile.convenient_time else "Не указано", 
                                             about=profile.about, goal=", ".join(profile.goals) if profile.goals else "Не указаны")
        )

        if profile.photo:
            try:
                await callback.message.answer_photo(
                    photo=profile.photo,
                    caption=profile_text,
                    reply_markup=keyboard)
                await callback.answer()
                return
            except:
                pass
        await callback.message.answer(
                    text=profile_text,
                    reply_markup=keyboard
                )

    else:
        await callback.message.answer(text=TEXT_NO_PROFILE, reply_markup=await get_back_to_menu())
    
    await callback.answer()


@router.callback_query(F.data.startswith("show_gallery_"))
async def show_gallery(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    parts = callback.data.split("_")
    user_id = parts[-2]
    game = parts[-1]

    nickname = (await repository.get_profile(user_id=int(user_id))).nickname
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Назад",
        callback_data=f"read_profile_other_{user_id}" if "filter" not in callback.data else f"read_profile_other_filter_{user_id}"
    )]])


    if games := await repository.get_games_by_user_id(user_id=int(user_id)):
        games = {game.name: game for game in games}
        if game in games:
            if games[game].gallery:
                media = [InputMediaPhoto(media=file_id) for file_id in games[game].gallery]
                await callback.bot.send_media_group(chat_id=callback.message.chat.id, media=media)
                await callback.message.answer(TEXT_GALLERY.format(name=nickname), reply_markup=kb)
                return
    await callback.message.answer(f"Упс, {nickname} не прикрепил фото игрового профиля", reply_markup=kb)
    
@router.callback_query(F.data == "delete_profile")
async def delete_profile(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(TEXT_CONFIRM_DELETE_PROFILE, reply_markup=await get_delete_confirm_kb())

async def delete_profile(callback: CallbackQuery):
    await callback.message.delete()
    await repository.delete_profile(user_id=callback.from_user.id)
    await callback.message.answer(text=TEXT_DELETE_PROFILE, reply_markup=await get_back_to_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("delete_confirm_"))
async def delete_profile_confirm(callback: CallbackQuery):
    await callback.answer()

    response = callback.data.split("_")[-1]

    if response == "yes":
        await delete_profile(callback)
    else:
        await update_profile_callback(callback)



@router.callback_query(F.data.in_(["deactivate_profile", "activate_profile"]))
async def deactivate_profile(callback: CallbackQuery):
    await callback.message.delete()

    if await repository.get_profile(user_id=callback.from_user.id):
        if callback.data == "deactivate_profile":
            await repository.deactivate_profile(user_id=callback.from_user.id)
            await callback.message.answer(text=TEXT_PROFILE_DEACTIVATED, reply_markup=await get_back_to_menu())
        else:
            await repository.activate_profile(user_id=callback.from_user.id)
            await callback.message.answer(text=TEXT_PROFILE_ACTIVATED, reply_markup=await get_back_to_menu())

    else:
        await callback.message.answer(text=TEXT_NO_PROFILE, reply_markup=await get_back_to_menu())

    await callback.answer()



