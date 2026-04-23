# middlewares/outer.py
"""
Внешние мидлвари для обработки апдейтов.

Для обратной совместимости UserValidationMiddleware реэкспортируется из
bot.middlewares.user_validation — реальный класс вынесен туда.
"""
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from shared.config import config
from shared.constants import SENSITIVE_TRADING_STATES
from shared.utils.logger import setup_logger

from bot.utils import get_event_user

logger = setup_logger()


def _mask_text(text: str | None, max_len: int = 50) -> str:
    """Простое маскирование: скрывает длинные строки и очевидные секреты."""
    if not text:
        return ""
    s = str(text)
    low = s.lower()
    # Если в тексте явно присутствуют слова 'password', 'api', 'token' или email — не выводим полностью
    if any(k in low for k in ("password", "pass", "api", "token", "secret", "@")):
        return "<hidden sensitive>"
    if len(s) > max_len:
        return s[:max_len//2] + "..." + s[-max_len//2:]
    return s


class AdminCheckMiddleware(BaseMiddleware):
    """Мидлварь для проверки прав администратора."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = get_event_user(event, data)

        # Добавляем флаг админа в data
        is_admin = False
        if user and user.id in config.ADMIN_IDS:
            is_admin = True

        data["is_admin"] = is_admin

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Мидлварь для логирования всех апдейтов."""
    
    # Состояния, в которых НЕ логируем текст сообщений
    SENSITIVE_STATES = SENSITIVE_TRADING_STATES
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = get_event_user(event, data)
        
        if user:
            # event — это Update (middleware на dp.update), достаём вложенные объекты
            msg = getattr(event, "message", None)
            callback = getattr(event, "callback_query", None)

            if msg and isinstance(msg, Message):
                # Проверяем текущее состояние
                state = data.get("state")
                current_state = None
                if state:
                    current_state = await state.get_state()
                
                # Если в чувствительном состоянии - не логируем текст
                if current_state in self.SENSITIVE_STATES:
                    logger.info(f"📨 Message from {user.id} (@{user.username}): <sensitive input hidden>")
                else:
                    logger.info(f"📨 Message from {user.id} (@{user.username}): {_mask_text(msg.text)}")
            elif callback and isinstance(callback, CallbackQuery):
                logger.info(f"🔘 Callback from {user.id} (@{user.username}): {_mask_text(callback.data)}")
        
        return await handler(event, data)


