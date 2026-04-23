# handlers/keyboards/common.py
from typing import Callable
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def common_back_kb(_: Callable) -> ReplyKeyboardMarkup:
    """Обычная кнопка 'Назад' для всех меню"""
    builder = ReplyKeyboardBuilder()
    builder.button(text=_("btn_back"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)