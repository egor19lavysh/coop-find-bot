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
    photo = State()
    is_active = State()



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