from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.profile_kb import *
from states.create_clan import *
from utils.creation_process import CMDS, restrict_access
from typing import Union
from handlers.clan.create_clan import TEXT_GAME, TEXT_DESCRIPTION


router = Router()


@router.message(ClanForm.raven_server)
@router.callback_query(ClanForm.raven_server)
async def raven_server_chosen(
    event: Union[CallbackQuery, Message],
    state: FSMContext
):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, SERVER_TEXT, get_raven_servers_kb, with_back=True)
            return
    else:
        callback = event

    await callback.answer()

    server = callback.data.split("_")[-1]

    if server == "back":
        await callback.message.delete()
        await callback.message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ClanForm.game)
        return
    
    data = await state.get_data()
    await state.update_data(name=data["name"] + "|" +server)
    await callback.message.edit_text(text=f"Выбран сервер: {server}", reply_markup=None)
    await callback.message.answer(text=TEXT_DESCRIPTION, reply_markup=ReplyKeyboardRemove())
    await state.set_state(ClanForm.description)