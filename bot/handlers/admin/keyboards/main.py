# handlers/admin/keyboards/main.py

# IMPORTS

from typing import Callable
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from shared.config import config

# ADMIN KEYBOARDS

def admin_main_kb(_: Callable) -> ReplyKeyboardMarkup:
    """Главное меню админ-панели"""
    rows = []
    webapp_url = (config.WEBAPP_BASE_URL or "").rstrip("/")
    if webapp_url:
        admin_url = webapp_url.rsplit("/webapp", 1)[0] + "/admin/"
        rows.append([KeyboardButton(text=_("btn_admin_web"), web_app=WebAppInfo(url=admin_url))])
    rows.append([KeyboardButton(text=_("btn_back"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


