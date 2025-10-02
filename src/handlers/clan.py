from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.clan_kb import *
from utils.constants import *
from repositories.clan_repository import clan_repository as repository
from handlers.create_clan import start_clan


router = Router()

class PhotoClanForm(StatesGroup):
    photo = State()

TEXT_INTRO = "Отлично! Что ты хочешь изменить в анкете клана?"
TEXT_YOUR_CHOICE = "Ты уверен? Знай, это твой выбор\n"
TEXT_NO_CLAN = "У тебя нет анкеты клана. Можешь создать ее командой /clan"
TEXT_DELETE_CLAN = "Твоя анкета клана удалена. Я не плачу, это просто пиксели."
TEXT_SEND_PHOTO = "Пришли новое фото клана в чат."
TEXT_PHOTO_UPDATED = "Фото клана обновлено."
TEXT_PHOTO_ERROR = 'Пришлите фотографию клана!'

@router.callback_query(F.data == "update_clan")
async def update_clan(callback: CallbackQuery):
    await callback.message.answer(text=TEXT_INTRO, reply_markup=(await get_update_clan_kb(user_id=callback.from_user.id)).as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("read_clan"))
async def read_clan(callback: CallbackQuery):

    callback_parts = callback.data.split("_")
    user_id = int(callback_parts[-1])
    type_user = callback_parts[-2]

    if clan := await repository.get_clan(user_id=user_id):

        keyboard = await get_interaction_kb(user_id=user_id) if type_user == "other" else None
        prefix = TEXT_YOUR_CHOICE if type_user == "other" else ""

        profile_text = prefix + CLAN_SAMPLE.format(
                    name=clan.name,
                    game=clan.game,
                    description=clan.description,
                    demands=clan.demands
        )

        if clan.photo:
            try:
                await callback.message.answer_photo(
                    photo=clan.photo,
                    caption=profile_text,
                    reply_markup=keyboard)
                await callback.answer()
                return
            except:
                pass
        await callback.message.answer(
                    text=profile_text + PHOTO_SAMPLE,
                    reply_markup=keyboard
                )

    else:
        await callback.message.answer(text=TEXT_NO_CLAN)
    
    await callback.answer() 

@router.callback_query(F.data == "recreate_clan")
async def recreate_clan(callback: CallbackQuery, state: FSMContext):
    await repository.delete_clan(user_id=callback.from_user.id)
    await state.update_data(
        user_id=callback.from_user.id
    )
    await start_clan(callback.bot, state)
    await callback.answer()

@router.callback_query(F.data == "delete_clan")
async def delete_clan(callback: CallbackQuery):
    await repository.delete_clan(user_id=callback.from_user.id)
    await callback.message.answer(text=TEXT_DELETE_CLAN)
    await callback.answer()

@router.callback_query(F.data == "update_clan_photo")
async def update_photo(callback: CallbackQuery, state: FSMContext):
    if await repository.get_clan(user_id=callback.from_user.id):
        await state.set_state(PhotoClanForm.photo)
        await callback.message.answer(text=TEXT_SEND_PHOTO)
    else:
        await callback.message.answer(text=TEXT_NO_CLAN)
    
    await callback.answer()


@router.message(PhotoClanForm.photo)
async def update_profile_photo(message: Message, state: FSMContext):
    if message.photo:
        await repository.update_clan_photo(user_id=message.from_user.id, new_photo=message.photo[-1].file_id)
        await message.answer(text=TEXT_PHOTO_UPDATED)
    else:
        await message.answer(text=TEXT_PHOTO_ERROR)

    await state.clear()