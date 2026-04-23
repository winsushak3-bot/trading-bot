# states/onboarding.py
from aiogram.fsm.state import State, StatesGroup


class OnboardingState(StatesGroup):
    language = State()
    nickname_input = State()
    nickname_confirm = State()
