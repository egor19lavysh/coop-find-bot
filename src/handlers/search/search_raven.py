from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.search import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.raven import *
from utils.constants import DONATE_TEXT
from keyboards.search_kb import get_games_filter_search_kb


router = Router()


@router.callback_query(SearchForm.raven_cluster)
async def raven_cluster_chosen(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    cluster = callback.data.split("_")[-1]

    if cluster == "back":
        await callback.message.delete()
        await callback.message.answer("Выберите игру:", reply_markup=await get_games_filter_search_kb())
        await state.set_state(SearchForm.game)
        return
    
    await state.update_data(raven_cluster=cluster)
    await callback.message.edit_text(
        text=f"Выбран кластер: {cluster}",
        reply_markup=None
    )

    await callback.message.answer(
        text=SERVER_TEXT,
        reply_markup=await get_raven_servers_kb(with_back=True, skip=True))
    await state.set_state(SearchForm.raven_server)

@router.callback_query(SearchForm.raven_server)
async def raven_server_chosen(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):
    await callback.answer()

    server = callback.data.split("_")[-1]

    if server == "back":
        await callback.message.delete()
        await callback.message.answer(
            text=CLUSTER_TEXT,
            reply_markup=await get_raven_clusters_kb(with_back=True, skip=True)
        )
        await state.set_state(SearchForm.raven_cluster)
        return
    
    await state.update_data(raven_server=server)
    await callback.message.edit_text(
        text=f"Выбран сервер: {server}",
        reply_markup=None
    )

    await callback.message.answer(
        text=CLASS_TEXT,
        reply_markup=await get_raven_classes_kb(with_back=True, skip=True))
    await state.set_state(SearchForm.raven_class)


@router.callback_query(SearchForm.raven_class)
async def raven_class_chosen(
    callback: Union[CallbackQuery, Message],
    state: FSMContext
):

    await callback.answer()

    char_class = callback.data.split("_")[-1]
    
    if char_class == "back":
        await callback.message.delete()
        await callback.message.answer(
            text=SERVER_TEXT,
            reply_markup=await get_raven_servers_kb(with_back=True, skip=True)
        )
        await state.set_state(SearchForm.raven_server)
        return
    
    await state.update_data(raven_class=char_class)
    await callback.message.edit_text(
        text=f"Выбран класс: {char_class}",
        reply_markup=None
    )

    await callback.message.answer(
        text=LEVEL_TEXT,
        reply_markup=await get_back_kb(skip=True))
    await state.set_state(SearchForm.raven_level)

@router.message(SearchForm.raven_level)
async def raven_level_entered(
    message: Message,
    state: FSMContext
):
    level_text = message.text.strip()

    if level_text == TEXT_BACK:
        await message.delete()
        await message.answer(
            text=CLASS_TEXT,
            reply_markup=await get_raven_classes_kb(with_back=True, skip=True)
        )
        await state.set_state(SearchForm.raven_class)
        return

    if level_text.lower() == "пропустить":
        await state.update_data(raven_level="skip")
        await message.answer(
            text="Уровень персонажа пропущен.",
            reply_markup=None
        )
        await message.answer(
            text=STATS_TEXT,
            reply_markup=await get_skip_keyboard(with_back=True))
        await state.set_state(SearchForm.raven_stats)
        return
    
    elif not level_text.isdigit():
        await message.answer(
            text="Уровень должен быть числом.",
            reply_markup=await get_back_kb(skip=True)
        )
        return

    level = int(level_text)

    await state.update_data(raven_level=level)
    await message.answer(
        text=f"Уровень персонажа установлен: {level}",
        reply_markup=None
    )

    await message.answer(
        text=STATS_TEXT,
        reply_markup=await get_skip_keyboard(with_back=True, skip=True))
    await state.set_state(SearchForm.raven_stats)

@router.message(SearchForm.raven_stats)
async def raven_stats_entered(
    message: Message,
    state: FSMContext
):
    stats_text = message.text.strip()

    if stats_text == TEXT_BACK:
        await message.delete()
        await message.answer(
            text=LEVEL_TEXT,
            reply_markup=await get_back_kb()
        )
        await state.set_state(SearchForm.raven_level)
        return

    if stats_text.lower() == "пропустить":
        await state.update_data(raven_stats="skip")
    else:
        stats_parts = stats_text.split("/")
        if len(stats_parts) != 3 or not all(part.strip().isdigit() for part in stats_parts):
            await message.answer(
                text="""Статы должны быть в формате 3 чисел через "/". Например: 480/500/666""",
                reply_markup=await get_skip_keyboard(with_back=True)
            )
            return

        await state.update_data(raven_stats=stats_text)
        
    await message.answer(DONATE_TEXT, reply_markup=await get_confirmation_kb(with_back=True, skip=True))
    await state.set_state(SearchForm.donate)
