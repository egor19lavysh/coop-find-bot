from aiogram.fsm.state import State, StatesGroup


class EditClanForm(StatesGroup):
    choose_field = State()
    name = State()
    game = State()
    description = State()
    demands = State()
    photo = State()

