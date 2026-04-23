"""
Shared bot setup helpers.

Используются и в polling-режиме (`bot/main.py`), и в webhook-режиме
(`backend/bot_webhook.py`), чтобы Dispatcher инициализировался идентично:
одни и те же middleware, routers, storage fallback.
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers import root_router
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.i18n import I18nMiddleware
from bot.middlewares.outer import (
    AdminCheckMiddleware,
    LoggingMiddleware,
)
from bot.middlewares.throttling import ThrottlingMiddleware
from shared.config import config
from shared.database.core import session_maker

logger = logging.getLogger(__name__)


async def build_storage() -> BaseStorage:
    """Redis с fallback на MemoryStorage при недоступности."""
    try:
        storage = RedisStorage.from_url(config.REDIS_URL)
        await storage.redis.ping()
        return storage
    except Exception as e:
        logger.warning("Redis unavailable, using MemoryStorage: %s", e)
        return MemoryStorage()


def build_bot() -> Bot:
    """Bot с дефолтными HTML parse_mode."""
    return Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher(storage: BaseStorage) -> Dispatcher:
    """
    Dispatcher с единым набором middleware и зарегистрированным root_router.
    Важно: порядок middleware имеет значение (logging -> db -> user -> admin -> i18n -> throttling).
    """
    dp = Dispatcher(storage=storage)

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware(AdminCheckMiddleware())
    dp.update.middleware(I18nMiddleware(storage=storage))
    dp.update.middleware(ThrottlingMiddleware(rate_limit=0.5, critical_rate_limit=3.0))

    dp.include_router(root_router)
    return dp
