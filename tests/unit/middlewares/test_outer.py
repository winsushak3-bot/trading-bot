# tests/unit/middlewares/test_outer.py
"""
Тесты для middlewares/outer.py
Проверяем AdminCheck, Logging, UserValidation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import User, Message, CallbackQuery

from bot.middlewares.outer import AdminCheckMiddleware, LoggingMiddleware, _mask_text


class TestMaskText:
    """Тесты функции маскирования."""
    
    def test_mask_password(self):
        """Тест: Маскирование пароля."""
        result = _mask_text("my_password_123")
        assert result == "<hidden sensitive>"
    
    def test_mask_api_key(self):
        """Тест: Маскирование API ключа."""
        result = _mask_text("api_key_12345")
        assert result == "<hidden sensitive>"
    
    def test_mask_email(self):
        """Тест: Маскирование email."""
        result = _mask_text("user@example.com")
        assert result == "<hidden sensitive>"
    
    def test_mask_long_text(self):
        """Тест: Обрезка длинного текста."""
        long_text = "A" * 100
        result = _mask_text(long_text, max_len=50)
        assert len(result) <= 53
    
    def test_mask_none(self):
        """Тест: None возвращает пустую строку."""
        result = _mask_text(None)
        assert result == ""
    
    def test_mask_normal_text(self):
        """Тест: Обычный текст не маскируется."""
        result = _mask_text("Hello World")
        assert result == "Hello World"


@pytest.mark.asyncio
class TestAdminCheckMiddleware:
    """Тесты AdminCheck middleware."""
    
    @pytest.fixture
    def middleware(self):
        return AdminCheckMiddleware()
    
    async def test_admin_flag_true_for_admin(self, middleware, mocker):
        """Тест: is_admin = True для админа."""
        mocker.patch("bot.middlewares.outer.config.ADMIN_IDS", [123])
        
        received_flag = None
        
        async def mock_handler(event, data):
            nonlocal received_flag
            received_flag = data.get("is_admin")
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Admin")
        mock_event = MagicMock()
        data = {"event_from_user": mock_user}
        
        await middleware(mock_handler, mock_event, data)
        
        assert received_flag is True
    
    async def test_admin_flag_false_for_user(self, middleware, mocker):
        """Тест: is_admin = False для обычного пользователя."""
        mocker.patch("bot.middlewares.outer.config.ADMIN_IDS", [123])
        
        received_flag = None
        
        async def mock_handler(event, data):
            nonlocal received_flag
            received_flag = data.get("is_admin")
            return "success"
        
        mock_user = User(id=456, is_bot=False, first_name="User")
        mock_event = MagicMock()
        data = {"event_from_user": mock_user}
        
        await middleware(mock_handler, mock_event, data)
        
        assert received_flag is False
    
    async def test_no_user_in_event(self, middleware):
        """Тест: Нет пользователя в событии."""
        async def mock_handler(event, data):
            return "success"
        
        mock_event = MagicMock()
        data = {}
        
        result = await middleware(mock_handler, mock_event, data)
        
        assert result == "success"
        assert data.get("is_admin") is False


@pytest.mark.asyncio
class TestLoggingMiddleware:
    """Тесты Logging middleware."""
    
    @pytest.fixture
    def middleware(self):
        return LoggingMiddleware()
    
    async def test_logs_message(self, middleware, mocker):
        """Тест: Логирование сообщения."""
        mock_logger = mocker.patch("bot.middlewares.outer.logger")
        
        async def mock_handler(event, data):
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test", username="testuser")
        mock_message = MagicMock(spec=Message)
        mock_message.text = "Hello"
        # Middleware работает на dp.update уровне: event — это Update
        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.callback_query = None
        data = {"event_from_user": mock_user}
        
        await middleware(mock_handler, mock_update, data)
        
        mock_logger.info.assert_called_once()
    
    async def test_logs_callback(self, middleware, mocker):
        """Тест: Логирование callback."""
        mock_logger = mocker.patch("bot.middlewares.outer.logger")
        
        async def mock_handler(event, data):
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test", username="testuser")
        mock_callback = CallbackQuery(
            id="1",
            from_user=mock_user,
            chat_instance="test",
            data="button_click"
        )
        # Middleware работает на dp.update уровне: event — это Update
        mock_update = MagicMock()
        mock_update.message = None
        mock_update.callback_query = mock_callback
        data = {"event_from_user": mock_user}
        
        await middleware(mock_handler, mock_update, data)
        
        mock_logger.info.assert_called_once()
    
    async def test_masks_sensitive_data(self, middleware, mocker):
        """Тест: Маскирование чувствительных данных."""
        mock_logger = mocker.patch("bot.middlewares.outer.logger")
        
        async def mock_handler(event, data):
            return "success"
        
        mock_user = User(id=123, is_bot=False, first_name="Test", username="testuser")
        mock_message = MagicMock(spec=Message)
        mock_message.text = "my_password_123"
        # Middleware работает на dp.update уровне: event — это Update
        mock_update = MagicMock()
        mock_update.message = mock_message
        mock_update.callback_query = None
        data = {"event_from_user": mock_user}
        
        await middleware(mock_handler, mock_update, data)
        
        call_args = str(mock_logger.info.call_args)
        assert "hidden" in call_args.lower() or "password" not in call_args.lower()
