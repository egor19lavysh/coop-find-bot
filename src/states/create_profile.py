from aiogram.fsm.state import State, StatesGroup


### ФОРМА ДЛЯ АНКЕТЫ
class ProfileForm(StatesGroup):
    nickname = State()
    telegram_tag = State()
    gender = State()
    game = State()
    rank = State()
    add_warcraft_mode = State()
    add_warcraft_rank = State()
    add_new_warcraft_rank = State()
    gallery = State()
    add_new_game = State()
    time = State()
    add_new_time = State()
    about = State()
    goal = State()
    add_new_goal = State()
    photo = State()
    check_profile = State()
    is_active = State()