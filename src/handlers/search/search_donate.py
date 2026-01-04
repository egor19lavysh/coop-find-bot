from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.search import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK, TEXT_GALLERY
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.raven import *
from utils.constants import DONATE_TEXT, BUDGET_TEXT, BUDGETS, TRANSFER_TEXT


router = Router()

@router.callback_query(SearchForm.donate)
async def donate_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()
    data = await state.get_data()

    choice = callback.data.split("_")[-1]

    if choice == "back":
        await callback.message.delete()
        game = data["game"]

        await callback.message.answer(
                text=STATS_TEXT,
                reply_markup=await get_skip_keyboard(with_back=True))
        
        if game == "Raven 2":
            await state.set_state(SearchForm.raven_stats)
        else:
            await state.set_state(SearchForm.lineage_stats)
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
        await state.set_state(SearchForm.budget)
    elif choice == "skip":
        await state.update_data(budget="skip")
        await callback.message.answer(text=TRANSFER_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
        await state.set_state(SearchForm.transfer)
    else:
        await state.update_data(budget="-")
        await callback.message.answer(text=TRANSFER_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
        await state.set_state(SearchForm.transfer)
    


@router.callback_query(SearchForm.budget)
async def budget_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    budget = callback.data.split("_")[-1]

    if budget == "back":
        await callback.message.answer(
            text=DONATE_TEXT,
            reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(SearchForm.donate)
        return
    
    await state.update_data(budget=budget)
    await callback.message.edit_text(
        text=f"Выбран бюджет: {budget}",
        reply_markup=None
    )

    await callback.message.answer(text=TRANSFER_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
    await state.set_state(SearchForm.transfer)
        

@router.callback_query(SearchForm.transfer)
async def transfer_handler(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    transfer = callback.data.split("_")[-1]

    if transfer == "back":
        await callback.message.answer(
            text=DONATE_TEXT,
            reply_markup=await get_confirmation_kb(with_back=True, skip=True))
        await state.set_state(SearchForm.donate)
        return

    await callback.message.edit_text(
        text=f"Выбран ответ: {transfer}",
        reply_markup=None
    )

    data = await state.get_data()
    game = data["game"]

    if game == "Raven 2":
        rank = f'{data["raven_cluster"]}@{data["raven_server"]}@{data["raven_class"]}@{data["raven_level"]}@{data["raven_stats"]}@{data["donate"]}@{data["budget"]}@{transfer}'
        await state.update_data(
            rank=rank
        )
    else:
        rank = f'{data["lineage_server"]}@{data["lineage_rasa"]}@{data["lineage_class"]}@{data["lineage_level"]}@{data["lineage_stats"]}@{data["donate"]}@{data["budget"]}@{transfer}'
        await state.update_data(
            rank=rank
        )

    await callback.message.answer("Выберите цель:", reply_markup=await get_goals_kb(True))
    await state.set_state(SearchForm.goal)

