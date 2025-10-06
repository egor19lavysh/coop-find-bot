from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile_kb import *
from utils.constants import *
from repositories.profile_repository import profile_repository as repository
from handlers.create_profile import start_profile


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
TEXT_YOUR_CHOICE = "Ты уверен? Знай, это твой выбор\n"


@router.message(Command("profile"))
async def update_profile(message: Message):
    await message.answer(text=TEXT_INTRO, reply_markup=(await get_profile_kb(user_id=message.from_user.id)).as_markup())

@router.callback_query(F.data == "profile")
async def update_profile_callback(callback: CallbackQuery):
    await callback.message.answer(text=TEXT_INTRO, reply_markup=(await get_profile_kb(user_id=callback.from_user.id)).as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("read_profile"))
async def read_profile(callback: CallbackQuery, state: FSMContext):

    callback_parts = callback.data.split("_")
    user_id = int(callback_parts[-1])
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
                user_rank = f"\n<b>Ранг:</b> {games[game]}"
            else:
                user_rank = f"\n<b>Ранг:</b> Не указан"

        else:
            user_rank = ""

        keyboard = await get_interaction_kb(user_id=user_id, game=game) if type_user == "other" else None
        prefix = TEXT_YOUR_CHOICE if type_user == "other" else ""

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
            add_info=PROFILE_ADD_INFO.format(about=profile.about, goal=profile.goal)
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
        await callback.message.answer(text=TEXT_NO_PROFILE)
    
    await callback.answer()


@router.callback_query(F.data == "delete_profile")
async def delete_profile(callback: CallbackQuery):
    await repository.delete_profile(user_id=callback.from_user.id)
    await callback.message.answer(text=TEXT_DELETE_PROFILE)
    await callback.answer()

@router.callback_query(F.data == "update_photo")
async def update_photo(callback: CallbackQuery, state: FSMContext):
    if await repository.get_profile(user_id=callback.from_user.id):
        await state.set_state(PhotoForm.photo)
        await callback.message.answer(text=TEXT_SEND_PHOTO)
    else:
        await callback.message.answer(text=TEXT_NO_PROFILE)
    
    await callback.answer()


@router.message(PhotoForm.photo)
async def update_profile_photo(message: Message, state: FSMContext):
    if message.photo:
        await repository.update_photo(user_id=message.from_user.id, photo=message.photo[-1].file_id)
        await message.answer(text=TEXT_PHOTO_UPDATED)
    else:
        await message.answer(text=TEXT_PHOTO_ERROR)

    await state.clear()

@router.callback_query(F.data.in_(["deactivate_profile", "activate_profile"]))
async def deactivate_profile(callback: CallbackQuery):
    if await repository.get_profile(user_id=callback.from_user.id):
        if callback.data == "deactivate_profile":
            await repository.deactivate_profile(user_id=callback.from_user.id)
            await callback.message.answer(text=TEXT_PROFILE_DEACTIVATED)
        else:
            await repository.activate_profile(user_id=callback.from_user.id)
            await callback.message.answer(text=TEXT_PROFILE_ACTIVATED)

    else:
        await callback.message.answer(text=TEXT_NO_PROFILE)

    await callback.answer()



