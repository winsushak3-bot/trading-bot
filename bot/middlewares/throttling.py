# middlewares/throttling.py
"""
Middleware для защиты от спама и rate limiting.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from collections import OrderedDict
import time
import logging

from shared.constants import SENSITIVE_TRADING_STATES
from bot.utils import get_event_user

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов от пользователей."""
    
    # Критичные состояния с более строгим rate limit
    CRITICAL_STATES = SENSITIVE_TRADING_STATES
    
    # Максимальный размер кэша для предотвращения утечки памяти
    MAX_CACHE_SIZE = 10000
    # Время жизни записи в кэше (1 час)
    CACHE_TTL_SECONDS = 3600
    
    def __init__(self, rate_limit: float = 0.5, critical_rate_limit: float = 3.0):
        """
        Args:
            rate_limit: Минимальное время между обычными запросами в секундах
            critical_rate_limit: Минимальное время между критичными операциями в секундах
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.critical_rate_limit = critical_rate_limit
        # OrderedDict для LRU eviction и контроля размера
        self.user_last_request: OrderedDict[tuple, float] = OrderedDict()
    
    def _cleanup_old_entries(self, current_time: float):
        """Удаляет устаревшие записи из кэша."""
        expired_keys = [
            key for key, timestamp in self.user_last_request.items()
            if current_time - timestamp > self.CACHE_TTL_SECONDS
        ]
        for key in expired_keys:
            del self.user_last_request[key]
    
    def _ensure_cache_size(self):
        """Удаляет самые старые записи если кэш превысил лимит."""
        while len(self.user_last_request) > self.MAX_CACHE_SIZE:
            # OrderedDict удаляет первый элемент при popitem(last=False)
            self.user_last_request.popitem(last=False)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = get_event_user(event, data)
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        current_time = time.time()
        
        # Очистка старых записей и контроль размера кэша
        self._cleanup_old_entries(current_time)
        self._ensure_cache_size()
        
        # Проверяем текущее состояние
        state = data.get("state")
        current_state = None
        if state:
            current_state = await state.get_state()
        
        # Определяем лимит в зависимости от состояния
        is_critical = current_state in self.CRITICAL_STATES
        limit = self.critical_rate_limit if is_critical else self.rate_limit
        request_key = (user_id, is_critical)
        
        # Проверяем, не слишком ли быстро пользователь отправляет запросы
        if request_key in self.user_last_request:
            time_passed = current_time - self.user_last_request[request_key]
            if time_passed < limit:
                # Слишком быстро - игнорируем запрос
                logger.warning(f"[THROTTLE] user_id={user_id}, critical={is_critical}, time_passed={time_passed:.2f}s")
                
                # Отправляем предупреждение только для сообщений
                # event — это Update (middleware на dp.update), достаём message
                msg = getattr(event, "message", None)
                if msg and isinstance(msg, Message):
                    try:
                        wait_time = max(1, int(limit - time_passed))
                        await msg.answer(f"⏱ Слишком быстро! Подождите {wait_time} секунд.")
                    except Exception as e:
                        logger.debug(f"Failed to send throttle message: {e}")
                
                return
        
        # Обновляем время последнего запроса
        self.user_last_request[request_key] = current_time
        
        return await handler(event, data)
