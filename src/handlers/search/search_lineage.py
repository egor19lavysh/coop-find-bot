from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.search import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.lineage import *
from utils.constants import DONATE_TEXT
from utils.raven import LEVEL_TEXT, STATS_TEXT
from keyboards.search_kb import get_games_filter_search_kb


router = Router()


@router.callback_query(SearchForm.lineage_server)
async def lineage_server_handler(
    callback: Union[Message, CallbackQuery],
    state: FSMContext,
):
    await callback.answer()

    server = callback.data.split("_")[-1]
    

    if server == "back":
        await callback.message.delete()
        await callback.message.answer("Выберите игру:", reply_markup=await get_games_filter_search_kb())
        await state.set_state(SearchForm.game)
        return

    await state.update_data(lineage_server=server)
    await callback.message.edit_text(
        text=f"Выбран сервер: {server}",
        reply_markup=None
    )

    await callback.message.answer(
        text=RASA_TEXT,
        reply_markup=await get_lineage_rases_kb(with_back=True, skip=True)
    )
    await state.set_state(SearchForm.lineage_rasa)

@router.callback_query(SearchForm.lineage_rasa)
async def lineage_rasa_handler(
    callback: Union[Message, CallbackQuery],
    state: FSMContext,
):
    await callback.answer()

    rasa = callback.data.split("_")[-1]

    if rasa == "back":
        await callback.message.answer(text=SERVER_TEXT, reply_markup=await get_lineage_servers_pt_1(with_back=True, skip=True))
        await state.set_state(SearchForm.lineage_server)
        return

    await state.update_data(lineage_rasa=rasa)
    await callback.message.edit_text(
        text=f"Выбрана раса: {rasa}",
        reply_markup=None
    )

    await callback.message.answer(
        text=CLASS_TEXT,
        reply_markup=await get_lineage_classes_kb(with_back=True, skip=True)
    )
    await state.set_state(SearchForm.lineage_class)

@router.callback_query(SearchForm.lineage_class)
async def lineage_class_handler(
    callback: Union[Message, CallbackQuery],
    state: FSMContext,
):
    await callback.answer()

    l_class = callback.data.split("_")[-1]

    if l_class == "back":
        await callback.message.answer(text=RASA_TEXT, reply_markup=await get_lineage_rases_kb(with_back=True, skip=True))
        await state.set_state(SearchForm.lineage_rasa)
        return

    await state.update_data(lineage_class=l_class)
    await callback.message.edit_text(
        text=f"Выбран класс: {l_class}",
        reply_markup=None
    )

    await callback.message.answer(
        text=LEVEL_TEXT,
        reply_markup=await get_back_kb(skip=True))
    await state.set_state(SearchForm.lineage_level)

@router.message(SearchForm.lineage_level)
async def lineage_level_entered(
    message: Message,
    state: FSMContext
):
    level_text = message.text.strip()

    if level_text == TEXT_BACK:
        await message.answer(
            text=CLASS_TEXT,
            reply_markup=await get_lineage_classes_kb(with_back=True, skip=True)
        )
        await state.set_state(SearchForm.lineage_class)
        return

    if level_text.lower() == "пропустить":
        await state.update_data(lineage_level="skip")
        await message.answer(
            text="Уровень персонажа пропущен.",
            reply_markup=None
        )
        await message.answer(
            text=STATS_TEXT,
            reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(SearchForm.lineage_stats)
        return
    
    elif not level_text.isdigit():
        await message.answer(
            text="Уровень должен быть числом.",
            reply_markup=await get_back_kb(skip=True)
        )
        return

    level = int(level_text)

    await state.update_data(lineage_level=level)
    await message.answer(
        text=f"Уровень персонажа установлен: {level}",
        reply_markup=None
    )

    await message.answer(
        text=STATS_TEXT,
        reply_markup=await get_skip_keyboard(with_back=True, skip=True)
    )
    await state.set_state(SearchForm.lineage_stats)

@router.message(SearchForm.lineage_stats)
async def lineage_stats_entered(
    message: Message,
    state: FSMContext
):  
    stats_text = message.text.strip()

    if stats_text == TEXT_BACK:
        await message.answer(
            text=LEVEL_TEXT,
            reply_markup=await get_back_kb(skip=True)
        )
        await state.set_state(SearchForm.lineage_level)
        return

    if stats_text.lower() == "пропустить":
        await state.update_data(lineage_stats="skip")
    else:
        stats_parts = stats_text.split("/")
        if len(stats_parts) != 3 or not all(part.strip().isdigit() for part in stats_parts):
            await message.answer(
                text="""Статы должны быть в формате 3 чисел через "/". Например: 480/500/666""",
                reply_markup=await get_skip_keyboard(with_back=True, skip=True)
            )
            return

        await state.update_data(lineage_stats=stats_text)
        
    await message.answer(DONATE_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
    await state.set_state(SearchForm.donate)
