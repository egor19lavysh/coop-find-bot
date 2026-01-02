from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.create_profile import *
from keyboards.profile_kb import *
from handlers.profile.create_profile import TEXT_GAME, TEXT_BACK
from utils.creation_process import restrict_access, CMDS
from typing import Union
from utils.lineage import *
from utils.constants import DONATE_TEXT
from utils.raven import LEVEL_TEXT, STATS_TEXT


router = Router()

@router.callback_query(F.data.startswith("get_lineage_servers_pt_"))
async def get_lineage_servers_handler(
    query: CallbackQuery,
):
    """Handler to send Lineage servers keyboard parts."""
    part = query.data.split("_")[-1]

    if part == "1":
        kb = await get_lineage_servers_pt_1(with_back=True)
    else:
        kb = await get_lineage_servers_pt_2(with_back=True)

    await query.message.edit_reply_markup(reply_markup=kb)


@router.message(ProfileForm.lineage_server)
@router.callback_query(ProfileForm.lineage_server)
async def lineage_server_handler(
    event: Union[Message, CallbackQuery],
    state: FSMContext,
):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, SERVER_TEXT, get_lineage_servers_pt_1, with_back=True)
            return
    else:
        callback = event

    await callback.answer()

    server = callback.data.split("_")[-1]

    if server == "back":
        await callback.message.answer(text=TEXT_GAME, reply_markup=await get_game_kb(with_back=True))
        await state.set_state(ProfileForm.game)
        return

    await state.update_data(lineage_server=server)
    await callback.message.edit_text(
        text=f"Выбран сервер: {server}",
        reply_markup=None
    )

    await callback.message.answer(
        text=RASA_TEXT,
        reply_markup=await get_lineage_rases_kb(with_back=True)
    )
    await state.set_state(ProfileForm.lineage_rasa)

@router.message(ProfileForm.lineage_rasa)
@router.callback_query(ProfileForm.lineage_rasa)
async def lineage_rasa_handler(
    event: Union[Message, CallbackQuery],
    state: FSMContext,
):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, RASA_TEXT, get_lineage_rases_kb, with_back=True)
            return
    else:
        callback = event

    await callback.answer()

    rasa = callback.data.split("_")[-1]

    if rasa == "back":
        await callback.message.answer(text=SERVER_TEXT, reply_markup=await get_lineage_servers_pt_1(with_back=True))
        await state.set_state(ProfileForm.lineage_server)
        return

    await state.update_data(lineage_rasa=rasa)
    await callback.message.edit_text(
        text=f"Выбрана раса: {rasa}",
        reply_markup=None
    )

    await callback.message.answer(
        text=CLASS_TEXT,
        reply_markup=await get_lineage_classes_kb(with_back=True)
    )
    await state.set_state(ProfileForm.lineage_class)

@router.message(ProfileForm.lineage_class)
@router.callback_query(ProfileForm.lineage_class)
async def lineage_class_handler(
    event: Union[Message, CallbackQuery],
    state: FSMContext,
):
    if isinstance(event, Message):
        if event.text in CMDS:
            await restrict_access(event, CLASS_TEXT, get_lineage_classes_kb, with_back=True)
            return
    else:
        callback = event

    await callback.answer()

    l_class = callback.data.split("_")[-1]

    if l_class == "back":
        await callback.message.answer(text=RASA_TEXT, reply_markup=await get_lineage_rases_kb(with_back=True))
        await state.set_state(ProfileForm.lineage_rasa)
        return

    await state.update_data(lineage_class=l_class)
    await callback.message.edit_text(
        text=f"Выбран класс: {l_class}",
        reply_markup=None
    )

    await callback.message.answer(
        text=LEVEL_TEXT,
        reply_markup=await get_back_kb())
    await state.set_state(ProfileForm.lineage_level)

@router.message(ProfileForm.lineage_level)
async def lineage_level_entered(
    message: Message,
    state: FSMContext
):
    if message.text in CMDS:
        await restrict_access(message, LEVEL_TEXT)
        return
    
    level_text = message.text.strip()

    if level_text == TEXT_BACK:
        await message.answer(
            text=CLASS_TEXT,
            reply_markup=await get_lineage_classes_kb(with_back=True)
        )
        await state.set_state(ProfileForm.lineage_class)
        return

    if not level_text.isdigit():
        await message.answer(
            text="Уровень должен быть числом.",
            reply_markup=await get_back_kb()
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
        reply_markup=await get_skip_keyboard(with_back=True))
    await state.set_state(ProfileForm.lineage_stats)

@router.message(ProfileForm.lineage_stats)
async def lineage_stats_entered(
    message: Message,
    state: FSMContext
):
    if message.text in CMDS:
        await restrict_access(message, STATS_TEXT, get_skip_keyboard, with_back=True)
        return
    
    stats_text = message.text.strip()

    if stats_text == TEXT_BACK:
        await message.answer(
            text=LEVEL_TEXT,
            reply_markup=await get_back_kb()
        )
        await state.set_state(ProfileForm.lineage_level)
        return

    if stats_text.lower() == "пропустить":
        await state.update_data(lineage_stats="-")
    else:
        stats_parts = stats_text.split("/")
        if len(stats_parts) != 3 or not all(part.strip().isdigit() for part in stats_parts):
            await message.answer(
                text="""Статы должны быть в формате 3 чисел через "/". Например: 480/500/666""",
                reply_markup=await get_skip_keyboard(with_back=True)
            )
            return

        await state.update_data(lineage_stats=stats_text)
        
    await message.answer(DONATE_TEXT, reply_markup=await get_confirmation_kb(with_back=True))
    await state.set_state(ProfileForm.donate)
