from aiogram.fsm.state import State, StatesGroup



class SendMessageForm(StatesGroup):
    message = State()

class GameForm(StatesGroup):
    search_type = State()
    game = State()
