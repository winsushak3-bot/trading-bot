# bot/utils.py
"""
Утилиты для Telegram-бот модуля.
"""
from typing import Optional
from aiogram.types import TelegramObject, User


def get_event_user(event: TelegramObject, data: dict) -> Optional[User]:
    """Извлечь пользователя из события или middleware data.

    Работает корректно для dp.update-уровня middleware, где event — Update.
    """
    return data.get("event_from_user") or getattr(event, "from_user", None)
