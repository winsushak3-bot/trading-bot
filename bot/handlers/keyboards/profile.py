# handlers/keyboards/profile.py
from typing import Callable
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from shared.utils.i18n import i18n

# --- REPLY (Нижние кнопки) ---

def profile_kb(_: Callable) -> ReplyKeyboardMarkup:
    """Клавиатура главного меню профиля"""
    builder = ReplyKeyboardBuilder()
    builder.button(text=_("btn_settings"))
    builder.button(text=_("btn_back"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def settings_kb(_: Callable) -> ReplyKeyboardMarkup:
    """Клавиатура настроек"""
    builder = ReplyKeyboardBuilder()
    builder.button(text=_("btn_language"))
    builder.button(text=_("btn_change_nick"))
    builder.button(text=_("btn_notifications"))
    builder.button(text=_("btn_back"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

# --- INLINE (Кнопки под сообщениями) ---

def language_inline_kb(_: Callable) -> InlineKeyboardMarkup:
    """Выбор языка"""
    builder = InlineKeyboardBuilder()
    builder.button(text=_("lang_ru"), callback_data="lang_ru")
    builder.button(text=_("lang_ua"), callback_data="lang_ua")
    builder.button(text=_("lang_en"), callback_data="lang_en")
    builder.adjust(1) 
    return builder.as_markup()

def language_confirm_kb(_: Callable, target_lang_code: str) -> InlineKeyboardMarkup:
    """Подтверждение смены языка"""
    builder = InlineKeyboardBuilder()
    confirm_text = i18n.get("btn_confirm", lang=target_lang_code)
    cancel_text = _("btn_cancel")
    builder.button(text=confirm_text, callback_data=f"conf_lang_{target_lang_code}")
    builder.button(text=cancel_text, callback_data="cancel_lang_change")
    builder.adjust(1)
    return builder.as_markup()

def change_nick_start_kb(_: Callable) -> InlineKeyboardMarkup:
    """Кнопка начала смены ника"""
    builder = InlineKeyboardBuilder()
    builder.button(text=_("btn_change_nick_action"), callback_data="start_change_nick")
    builder.adjust(1)
    return builder.as_markup()

def confirm_nick_kb(_: Callable) -> InlineKeyboardMarkup:
    """Подтверждение нового ника"""
    builder = InlineKeyboardBuilder()
    builder.button(text=_("nick_btn_confirm"), callback_data="confirm_new_nick")
    builder.button(text=_("btn_cancel"), callback_data="cancel_change_nick")
    builder.adjust(1)
    return builder.as_markup()

def notifications_kb(_: Callable, is_enabled: bool) -> InlineKeyboardMarkup:
    """Переключатель уведомлений"""
    builder = InlineKeyboardBuilder()
    if is_enabled:
        text = _("btn_toggle_off")
        data = "notif_disable"
    else:
        text = _("btn_toggle_on")
        data = "notif_enable"
    builder.button(text=text, callback_data=data)
    builder.adjust(1)
    return builder.as_markup()