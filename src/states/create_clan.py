from aiogram.fsm.state import State, StatesGroup


class ClanForm(StatesGroup):
    name = State()
    game = State()

    # RAVEN
    raven_server = State()

    # LINEAGE
    lineage_server = State()
    
    description = State()
    demands = State()
    photo = State()
    check = State()