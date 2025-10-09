from aiogram.fsm.state import State, StatesGroup


### ФОРМА ДЛЯ АНКЕТЫ
class ProfileForm(StatesGroup):
    nickname = State()
    telegram_tag = State()
    gender = State()
    game = State()
    rank = State()
    add_new_game = State()
    about = State()
    goal = State()
    photo = State()
    check_profile = State()
    is_active = State()