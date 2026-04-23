# middlewares/i18n.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.storage.base import BaseStorage

from shared.utils.i18n import i18n
from shared.database.repo.users import UserRepo
from shared.utils.cache import get_user_lang, set_user_lang

class I18nMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage):
        super().__init__()
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        
        # 1. Пытаемся достать юзера безопасно
        telegram_user: User = data.get("event_from_user")
        if not telegram_user:
            telegram_user = getattr(event, "from_user", None)
        
        user_lang = None
        
        # 2. Пытаемся достать язык из Redis (КЕШ) через утилиту
        redis = getattr(self.storage, "redis", None)

        if redis and telegram_user:
            user_lang = await get_user_lang(redis, telegram_user.id)

        # 3. Если в кеше пусто — идем в Базу Данных
        if not user_lang and session and telegram_user:
            repo = UserRepo(session)
            user = await repo.get_user(telegram_user.id)
            if user:
                user_lang = user.language
                
                # Сохраняем найденное в Redis С TTL (24 часа)
                if redis:
                    await set_user_lang(redis, telegram_user.id, user_lang)
            else:
                user_lang = "ru" # Дефолтный язык

        # Если совсем ничего не нашли, ставим русский
        if not user_lang:
            user_lang = "ru"

        # Функция перевода
        def get_text(key: str, **kwargs):
            return i18n.get(key, lang=user_lang, **kwargs)

        data["_"] = get_text
        
        return await handler(event, data)