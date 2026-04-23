# tests/unit/middlewares/test_i18n.py
"""
Тесты для middlewares/i18n.py
КРИТИЧНО! Проверяем что переводы работают.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import User

from bot.middlewares.i18n import I18nMiddleware


@pytest.mark.asyncio
class TestI18nMiddleware:
    """Тесты I18n middleware."""
    
    @pytest.fixture
    def storage(self):
        """Фикстура storage."""
        storage = MagicMock()
        storage.redis = AsyncMock()
        return storage
    
    @pytest.fixture
    def middleware(self, storage):
        """Фикстура middleware."""
        return I18nMiddleware(storage)
    
    async def test_language_loaded_from_redis(self, middleware, storage):
        """Тест: Язык загружается из Redis (кеш)."""
        storage.redis.get = AsyncMock(return_value=b"en")
        
        received_lang = None
        
        async def mock_handler(event, data):
            nonlocal received_lang
            translate = data.get("_")
            received_lang = "en" if translate else None
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test")
        mock_event = MagicMock()
        data = {"event_from_user": mock_user, "session": AsyncMock()}
        
        await middleware(mock_handler, mock_event, data)
        
        storage.redis.get.assert_called_once_with("lang:123")
        assert "_" in data
    
    async def test_language_loaded_from_db_if_not_in_cache(self, middleware, storage, mocker):
        """Тест: Язык загружается из БД если нет в кеше."""
        storage.redis.get = AsyncMock(return_value=None)
        storage.redis.set = AsyncMock()
        
        mock_user_obj = MagicMock()
        mock_user_obj.language = "ua"
        
        mock_repo = MagicMock()
        mock_repo.get_user = AsyncMock(return_value=mock_user_obj)
        
        mocker.patch("bot.middlewares.i18n.UserRepo", return_value=mock_repo)
        
        async def mock_handler(event, data):
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test")
        mock_event = MagicMock()
        mock_session = AsyncMock()
        data = {"event_from_user": mock_user, "session": mock_session}
        
        await middleware(mock_handler, mock_event, data)
        
        mock_repo.get_user.assert_called_once_with(123)
        storage.redis.set.assert_called_once()
    
    async def test_default_language_for_new_user(self, middleware, storage, mocker):
        """Тест: Дефолтный язык (ru) для нового пользователя."""
        storage.redis.get = AsyncMock(return_value=None)
        
        mock_repo = MagicMock()
        mock_repo.get_user = AsyncMock(return_value=None)
        
        mocker.patch("bot.middlewares.i18n.UserRepo", return_value=mock_repo)
        
        received_translate = None
        
        async def mock_handler(event, data):
            nonlocal received_translate
            received_translate = data.get("_")
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test")
        mock_event = MagicMock()
        mock_session = AsyncMock()
        data = {"event_from_user": mock_user, "session": mock_session}
        
        await middleware(mock_handler, mock_event, data)
        
        assert received_translate is not None
    
    async def test_translation_function_works(self, middleware, storage, mocker):
        """Тест: Функция перевода работает."""
        storage.redis.get = AsyncMock(return_value=b"ru")
        
        mock_i18n = MagicMock()
        mock_i18n.get = MagicMock(return_value="Привет")
        
        mocker.patch("bot.middlewares.i18n.i18n", mock_i18n)
        
        received_text = None
        
        async def mock_handler(event, data):
            nonlocal received_text
            translate = data.get("_")
            received_text = translate("hello")
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test")
        mock_event = MagicMock()
        data = {"event_from_user": mock_user, "session": AsyncMock()}
        
        await middleware(mock_handler, mock_event, data)
        
        assert received_text == "Привет"
    
    async def test_no_user_in_event(self, middleware, storage):
        """Тест: Нет пользователя в событии."""
        async def mock_handler(event, data):
            return "success"
        
        mock_event = MagicMock()
        data = {}
        
        result = await middleware(mock_handler, mock_event, data)
        
        assert result == "success"
        assert "_" in data
