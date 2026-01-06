from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.edit_profile import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK, TEXT_GALLERY
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.raven import *
from utils.constants import DONATE_TEXT, BUDGET_TEXT, BUDGETS, TRANSFER_TEXT
from repositories.profile_repository import profile_repository as repository


router = Router()

TEXT_SUCCESS_EDIT = "Изменения успешно сохранены! ✅"
TEXT_BACK_TO_MENU = "Вернуться назад?"


@router.callback_query(EditProfileForm.donate)
async def donate_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    choice = callback.data.split("_")[-1]

    if choice == "back":
        await callback.message.delete()
        data = await state.get_data()
        game = data["game"]

        await callback.message.answer(
                text=STATS_TEXT,
                reply_markup=await get_skip_keyboard(with_back=True))
        
        if game == "Raven 2":
            await state.set_state(EditProfileForm.raven_stats)
        else:
            await state.set_state(EditProfileForm.lineage_stats)
        return
    
    await state.update_data(donate=choice)
    await callback.message.edit_text(
        text=f"Выбран вариант: {choice}",
        reply_markup=None
    )

    if choice == "Да":
        await callback.message.answer(
            text=BUDGET_TEXT,
            reply_markup=await get_raven_budgets_kb(with_back=True))
        await state.set_state(EditProfileForm.budget)
    else:
        await state.update_data(budget="-")
        await callback.message.answer(text=TRANSFER_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
        await state.set_state(EditProfileForm.transfer)
    


@router.callback_query(EditProfileForm.budget)
async def budget_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    budget = callback.data.split("_")[-1]

    if budget == "back":
        await callback.message.delete()
        await callback.message.answer(
            text=DONATE_TEXT,
            reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(EditProfileForm.donate)
        return
    
    await state.update_data(budget=budget)
    await callback.message.edit_text(
        text=f"Выбран бюджет: {budget}",
        reply_markup=None
    )

    await callback.message.answer(text=TRANSFER_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
    await state.set_state(EditProfileForm.transfer)
        

@router.callback_query(EditProfileForm.transfer)
async def transfer_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    transfer = callback.data.split("_")[-1]

    if transfer == "back":
        await callback.message.delete()
        await callback.message.answer(
            text=DONATE_TEXT,
            reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(EditProfileForm.donate)
        return
    elif transfer == "skip":
        transfer = "-"

    await callback.message.edit_text(
        text=f"Выбран ответ: {transfer if transfer != '-' else 'Пропустить'}",
        reply_markup=None
    )

    data = await state.get_data()
    game = data["game"]

    if game == "Raven 2":
        rank = f'{data["raven_cluster"]}@{data["raven_server"]}@{data["raven_class"]}@{data["raven_level"]}@{data["raven_stats"]}@{data["donate"]}@{data["budget"]}@{transfer}'
        await state.update_data(
            game_rank=rank
        )
    else:
        rank = f'{data["lineage_server"]}@{data["lineage_rasa"]}@{data["lineage_class"]}@{data["lineage_level"]}@{data["lineage_stats"]}@{data["donate"]}@{data["budget"]}@{transfer}'
        await state.update_data(
            game_rank=rank
        )

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
            await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(False))
            await state.set_state(EditProfileForm.gallery)

