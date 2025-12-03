from aiogram.fsm.state import State, StatesGroup


class EditProfileForm(StatesGroup):
    choose_field = State()
    nickname = State()
    telegram_tag = State()
    gender = State()
    games = State()
    rank = State()
    time = State()
    add_new_time = State()
    add_new_game = State()
    add_warcraft_mode = State()
    add_warcraft_rank = State()
    add_new_warcraft_rank = State()
    gallery = State()
    about = State()
    goal = State()
    add_new_goal = State()
    photo = State()
    is_active = State()
    clear = State()
    num_rank = State()



