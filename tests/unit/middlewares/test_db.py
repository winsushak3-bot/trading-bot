# tests/unit/middlewares/test_db.py
"""
Тесты для middlewares/db.py
КРИТИЧНО! Если middleware сломается, весь бот упадет.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User

from bot.middlewares.db import DbSessionMiddleware


@pytest.mark.asyncio
class TestDbSessionMiddleware:
    """Тесты DB middleware."""
    
    @pytest.fixture
    def session_pool(self):
        """Фикстура session pool."""
        pool = MagicMock()
        return pool
    
    @pytest.fixture
    def middleware(self, session_pool):
        """Фикстура middleware."""
        return DbSessionMiddleware(session_pool)
    
    async def test_session_injected_into_handler(self, middleware, session_pool):
        """Тест: Сессия передается в handler."""
        mock_session = AsyncMock()
        session_pool.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        session_pool.return_value.__aexit__ = AsyncMock(return_value=None)
        
        handler_called = False
        received_session = None
        
        async def mock_handler(event, data):
            nonlocal handler_called, received_session
            handler_called = True
            received_session = data.get("session")
            return "success"
        
        mock_event = MagicMock()
        data = {}
        
        result = await middleware(mock_handler, mock_event, data)
        
        assert handler_called
        assert received_session is mock_session
        assert result == "success"
    
    async def test_session_closed_after_handler(self, middleware, session_pool):
        """Тест: Сессия закрывается после обработки."""
        mock_session = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        session_pool.return_value = mock_context
        
        async def mock_handler(event, data):
            return "success"
        
        mock_event = MagicMock()
        data = {}
        
        await middleware(mock_handler, mock_event, data)
        
        mock_context.__aexit__.assert_called_once()
    
    async def test_session_closed_on_error(self, middleware, session_pool):
        """Тест: Сессия закрывается даже при ошибке в handler."""
        mock_session = AsyncMock()
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        session_pool.return_value = mock_context
        
        async def mock_handler(event, data):
            raise ValueError("Test error")
        
        mock_event = MagicMock()
        data = {}
        
        with pytest.raises(ValueError):
            await middleware(mock_handler, mock_event, data)
        
        mock_context.__aexit__.assert_called_once()
    
    async def test_multiple_handlers_get_different_sessions(self, middleware, session_pool):
        """Тест: Каждый handler получает свою сессию."""
        sessions_received = []
        
        async def mock_handler(event, data):
            sessions_received.append(data.get("session"))
            return "success"
        
        mock_session1 = AsyncMock()
        mock_session2 = AsyncMock()
        
        mock_context1 = AsyncMock()
        mock_context1.__aenter__ = AsyncMock(return_value=mock_session1)
        mock_context1.__aexit__ = AsyncMock(return_value=None)
        
        mock_context2 = AsyncMock()
        mock_context2.__aenter__ = AsyncMock(return_value=mock_session2)
        mock_context2.__aexit__ = AsyncMock(return_value=None)
        
        session_pool.side_effect = [mock_context1, mock_context2]
        
        await middleware(mock_handler, MagicMock(), {})
        await middleware(mock_handler, MagicMock(), {})
        
        assert len(sessions_received) == 2
        assert sessions_received[0] is mock_session1
        assert sessions_received[1] is mock_session2
