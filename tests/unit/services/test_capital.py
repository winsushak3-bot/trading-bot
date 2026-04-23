# tests/unit/services/test_capital.py
"""
Тесты для services/capital.py
КРИТИЧНО! Проверяем работу с биржей БЕЗ реальных запросов.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientTimeout

from shared.services.capital import CapitalClient


@pytest.mark.asyncio
class TestCapitalClient:
    """Тесты клиента Capital.com API."""
    
    @pytest.fixture
    def client(self):
        """Фикстура клиента."""
        return CapitalClient()
    
    async def test_check_connection_success(self, client, mocker):
        """Тест: Успешное подключение (200 OK)."""
        mock_response_auth = MagicMock()
        mock_response_auth.status = 200
        mock_response_auth.headers = {
            "CST": "test_cst_token",
            "X-SECURITY-TOKEN": "test_security_token"
        }
        mock_response_auth.__aenter__ = AsyncMock(return_value=mock_response_auth)
        mock_response_auth.__aexit__ = AsyncMock(return_value=None)
        
        mock_response_accounts = MagicMock()
        mock_response_accounts.status = 200
        mock_response_accounts.json = AsyncMock(return_value={
            "accounts": [{
                "balance": {
                    "balance": 10000.0,
                    "currency": "USD",
                    "available": 9500.0,
                    "profitLoss": 0.0
                }
            }]
        })
        mock_response_accounts.__aenter__ = AsyncMock(return_value=mock_response_accounts)
        mock_response_accounts.__aexit__ = AsyncMock(return_value=None)
        
        mock_response_positions = MagicMock()
        mock_response_positions.status = 200
        mock_response_positions.json = AsyncMock(return_value={
            "positions": []
        })
        mock_response_positions.__aenter__ = AsyncMock(return_value=mock_response_positions)
        mock_response_positions.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response_auth)
        mock_session.get = MagicMock(side_effect=[mock_response_accounts, mock_response_positions])
        mock_session.closed = False
        
        mocker.patch.object(client, '_get_session', return_value=mock_session)
        
        result, error = await client.check_connection("test@example.com", "password", "api_key")
        
        assert error is None
        assert result is not None
        assert result["balance"] == 10000.0
        assert result["currency"] == "USD"
        assert result["available"] == 9500.0
    
    async def test_check_connection_auth_error_401(self, client, mocker):
        """Тест: Ошибка авторизации (401 Unauthorized)."""
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)
        mock_session.closed = False
        
        mocker.patch.object(client, '_get_session', return_value=mock_session)
        
        result, error = await client.check_connection("wrong@example.com", "wrong_pass", "wrong_key")
        
        assert result is None
        assert error is not None
    
    async def test_close_session(self, client, mocker):
        """Тест: Закрытие сессии."""
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session.closed = False
        
        client._session = mock_session
        
        await client.close()
        
        mock_session.close.assert_called_once()
    
    async def test_get_session_creates_new(self, client):
        """Тест: _get_session создает новую сессию если её нет."""
        assert client._session is None
        
        session = client._get_session()
        
        assert session is not None
        assert client._session is not None
    
    async def test_get_session_reuses_existing(self, client, mocker):
        """Тест: _get_session переиспользует существующую сессию."""
        mock_session = AsyncMock()
        mock_session.closed = False
        
        client._session = mock_session
        
        session = client._get_session()
        
        assert session is mock_session
