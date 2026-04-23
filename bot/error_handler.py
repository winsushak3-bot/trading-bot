"""
Global error handler для aiogram Dispatcher.

Единый для polling (bot/main.py) и webhook (backend/bot_webhook.py) режимов:
- логирует traceback
- алертит администраторов в Telegram
- отвечает пользователю локализованным текстом
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from shared.utils.i18n import i18n
from shared.config import config

logger = logging.getLogger(__name__)


def register_error_handler(dp: Dispatcher, bot: Bot) -> None:
    """Зарегистрировать глобальный @dp.error() handler на переданный dispatcher."""

    @dp.error()
    async def _global_error_handler(event: ErrorEvent) -> None:
        logger.exception("❌ Critical error: %s", event.exception)

        # 1. Алерт админам
        error_text = (
            f"🚨 ERROR\n\n"
            f"Type: {type(event.exception).__name__}\n"
            f"Message: {str(event.exception)[:500]}"
        )
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(admin_id, error_text)
            except Exception as e:
                logger.error("Failed to notify admin %s: %s", admin_id, e)

        # 2. Ответ пользователю (определяем язык из update)
        user_lang = "ru"
        tg_user = None
        if event.update.message:
            tg_user = event.update.message.from_user
        elif event.update.callback_query:
            tg_user = event.update.callback_query.from_user
        if tg_user and tg_user.language_code:
            code = tg_user.language_code[:2]
            if code in ("ru", "en", "ua"):
                user_lang = code

        try:
            if event.update.message:
                await event.update.message.answer(i18n.get("error_technical", lang=user_lang))
            elif event.update.callback_query:
                await event.update.callback_query.answer(
                    i18n.get("error_system", lang=user_lang),
                    show_alert=True,
                )
        except Exception as e:
            logger.error("Failed to notify user: %s", e)
