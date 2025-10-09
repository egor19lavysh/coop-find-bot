from aiogram.fsm.state import State, StatesGroup


class ClanForm(StatesGroup):
    name = State()
    game = State()
    description = State()
    demands = State()
    photo = State()
    check = State()