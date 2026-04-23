# states/admin.py
from aiogram.fsm.state import StatesGroup, State



class AdminState(StatesGroup):
    # Главное меню админ-панели
    main = State()
