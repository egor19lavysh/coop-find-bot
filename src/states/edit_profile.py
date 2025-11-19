from aiogram.fsm.state import State, StatesGroup


class EditProfileForm(StatesGroup):
    choose_field = State()
    nickname = State()
    telegram_tag = State()
    gender = State()
    games = State()
    rank = State()
    add_new_game = State()
    about = State()
    goal = State()
    add_new_goal = State()
    photo = State()
    is_active = State()



