# handlers/keyboards/main_menu.py
from typing import Callable
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb(_: Callable, user_id: int, is_admin: bool | None = None) -> ReplyKeyboardMarkup:
    """
    Главное меню.

    :param _: функция перевода
    :param user_id: ID пользователя (на будущее, если понадобится)
    :param is_admin: флаг администратора. Если True — добавляем кнопку админ-панели.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=_("btn_profile"))

    # Кнопка "Админ панель" доступна только администраторам
    if is_admin:
        builder.button(text=_("btn_admin_panel"))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)