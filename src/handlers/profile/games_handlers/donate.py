from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.create_profile import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK, TEXT_GALLERY
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.raven import *
from utils.constants import DONATE_TEXT, BUDGET_TEXT, BUDGETS


router = Router()


@router.callback_query(ProfileForm.donate)
async def donate_handler(
    event: Union[CallbackQuery, Message],
    state: FSMContext
):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, DONATE_TEXT, get_confirmation_kb, with_back=True)
            return
    else:
        callback = event

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
            await state.set_state(ProfileForm.raven_stats)
        else:
            await state.set_state(ProfileForm.lineage_stats)
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
        await state.set_state(ProfileForm.budget)
    else:
        if game == "Raven 2":
            rank = f'{data["raven_cluster"]}${data["raven_server"]}${data["raven_class"]}${data["raven_level"]}${data["raven_stats"]}${choice}$-'
            print(rank)
            await state.update_data(
                game_rank=rank
            )
        else:
            rank = f'{data["lineage_server"]}${data["lineage_rasa"]}${data["lineage_class"]}${data["lineage_level"]}${data["lineage_stats"]}${choice}$-'
            print(rank)
            await state.update_data(
                game_rank=rank
            )

        await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(ProfileForm.gallery)


@router.callback_query(ProfileForm.budget)
async def budget_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    budget = callback.data.split("_")[-1]

    if budget == "back":
        await callback.message.answer(
            text=DONATE_TEXT,
            reply_markup=await get_confirmation_kb(with_back=True))
        await state.set_state(ProfileForm.donate)
        return
    
    await state.update_data(budget=budget)
    await callback.message.edit_text(
        text=f"Выбран бюджет: {budget}",
        reply_markup=None
    )

    data = await state.get_data()
    game = data["game"]

    if game == "Raven 2":
        rank = f'{data["raven_cluster"]}/{data["raven_server"]}/{data["raven_class"]}/{data["raven_level"]}/{data["raven_stats"]}/Да/{budget}'
        print(rank)
        await state.update_data(
            game_rank=rank
        )
    else:
        rank = f'{data["lineage_server"]}/{data["lineage_rasa"]}/{data["lineage_class"]}/{data["lineage_level"]}/{data["lineage_stats"]}/Да/{budget}'
        print(rank)
        await state.update_data(
            game_rank=rank
        )

    await callback.message.answer(text=TEXT_GALLERY, reply_markup=await get_skip_keyboard(with_back=True))
    await state.set_state(ProfileForm.gallery)
        


