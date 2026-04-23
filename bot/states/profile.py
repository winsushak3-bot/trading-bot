# states/profile.py
from aiogram.fsm.state import State, StatesGroup


class ProfileState(StatesGroup):
    main = State()
    settings = State()
    language = State()
    settings_notifications = State()
    nick_change_input = State()
    nick_change_confirm = State()
