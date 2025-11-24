from aiogram.fsm.state import State, StatesGroup



class SendMessageForm(StatesGroup):
    message = State()

class GameForm(StatesGroup):
    search_type = State()
    game = State()

class SearchForm(StatesGroup):
    game = State()
    warcraft_mode = State()
    warcraft_rank = State()
    mode = State()
    rank = State()
    goal = State()