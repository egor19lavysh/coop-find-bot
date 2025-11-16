from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.clan_kb import *
from utils.constants import *
from repositories.clan_repository import clan_repository as repository
from .create_clan import start_clan


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

@router.message(Command("clan"))
async def update_clan(message: Message):
    await message.delete()
    await message.answer(text=TEXT_INTRO, reply_markup=(await get_clan_menu_kb()))

@router.callback_query(F.data == "clan")
async def update_clan_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=TEXT_INTRO, reply_markup=(await get_clan_menu_kb()))
    await callback.answer()

@router.callback_query(F.data == "get_all_user_clans")
async def get_all_user_clans(callback: CallbackQuery):
    await callback.message.delete()

    user_id = callback.from_user.id
    await callback.answer()
    if clans := await repository.get_clans(user_id=user_id):
        await callback.message.answer(text="Вот все твои кланы:", reply_markup=await get_clans_kb(clans))
    else:
        await callback.message.answer(text="У тебя еще нет кланов. Создай его в меню /clan")


@router.callback_query(F.data.startswith("detail_clan_"))
async def detail_clan(callback: CallbackQuery):
    await callback.message.delete()

    clan_id = int(callback.data.split("_")[-1])
    await callback.answer()

    if clan := await repository.get_clan_by_id(clan_id=clan_id):
        await callback.message.answer(text=f"Вот твой клан {clan.name}:", reply_markup=await get_update_clan_kb(clan_id=clan_id))
    else:
        await callback.message.answer(text="Что-то пошло не так... Попробуйте позже")


@router.callback_query(F.data.startswith("read_clan"))
async def read_clan(callback: CallbackQuery):
    await callback.message.delete()

    callback_parts = callback.data.split("_")
    clan_id = int(callback_parts[-1])
    type_user = callback_parts[-2]

    if clan := await repository.get_clan_by_id(clan_id=clan_id):

        keyboard = await get_interaction_kb(user_id=clan.user_id, game=clan.game) if type_user == "other" else await get_back_to_menu(clan_id)
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

# @router.callback_query(F.data.startswith("recreate_clan"))
# async def recreate_clan(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()

#     clan_id = int(callback.data.split("_")[-1])
#     await repository.delete_clan(clan_id=clan_id)
#     await state.update_data(
#         user_id=callback.from_user.id
#     )
#     await start_clan(callback.bot, state)
#     await callback.answer()

@router.callback_query(F.data.startswith("delete_clan"))
async def delete_clan(callback: CallbackQuery):
    await callback.message.delete()

    clan_id = int(callback.data.split("_")[-1])
    await repository.delete_clan(clan_id=clan_id)
    await callback.message.answer(text=TEXT_DELETE_CLAN, reply_markup=await get_back_to_clans())
    await callback.answer()

# @router.callback_query(F.data.startswith("update_clan_photo"))
# async def update_photo(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()


#     clan_id = int(callback.data.split("_")[-1])
#     if await repository.get_clan_by_id(clan_id=clan_id):
#         await state.update_data(clan_id=clan_id)
#         await state.set_state(PhotoClanForm.photo)
#         await callback.message.answer(text=TEXT_SEND_PHOTO)
#     else:
#         await callback.message.answer(text=TEXT_NO_CLAN, reply_markup=await get_back_to_menu(clan_id))
    
#     await callback.answer()


# @router.message(PhotoClanForm.photo)
# async def update_profile_photo(message: Message, state: FSMContext):
#     if message.photo:
#         data = await state.get_data()
#         await repository.update_clan_photo(clan_id=data["clan_id"], new_photo=message.photo[-1].file_id)
#         await message.answer(text=TEXT_PHOTO_UPDATED, reply_markup=await get_back_to_menu(data["clan_id"]))
#     else:
#         await message.answer(text=TEXT_PHOTO_ERROR)

#     await state.clear()