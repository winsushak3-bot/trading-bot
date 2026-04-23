# utils/cache.py
"""
Централизованные утилиты для работы с Redis кэшем.
Устраняет дублирование логики кэширования в разных модулях.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# TTL по умолчанию для разных типов кэша
LANG_CACHE_TTL = 86400  # 24 часа


async def get_user_lang(redis, user_id: int) -> Optional[str]:
    """Получает язык пользователя из Redis кэша."""
    if not redis:
        return None
    try:
        lang = await redis.get(f"lang:{user_id}")
        return lang.decode() if lang else None
    except Exception as e:
        logger.debug(f"Redis get lang failed for user {user_id}: {e}")
        return None


async def set_user_lang(redis, user_id: int, lang: str, ttl: int = LANG_CACHE_TTL) -> bool:
    """Сохраняет язык пользователя в Redis кэш с TTL."""
    if not redis:
        return False
    try:
        await redis.set(f"lang:{user_id}", lang, ex=ttl)
        return True
    except Exception as e:
        logger.debug(f"Redis set lang failed for user {user_id}: {e}")
        return False
