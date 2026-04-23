# services/capital.py

# IMPORTS

import aiohttp
import logging
import asyncio
from typing import Tuple, Optional, Dict, Any
from shared.constants import CAPITAL_API_TIMEOUT_SECONDS, CAPITAL_BASE_URL

logger = logging.getLogger(__name__)

# CAPITAL.COM API CLIENT

class CapitalClient:
    """
    Клиент для работы с Capital.com API (Demo).
    Документация: https://open-api.capital.com/
    """
    BASE_URL = CAPITAL_BASE_URL
    
    def __init__(self):
        self._session = None
    
    def _get_session(self):
        """Ленивая инициализация сессии."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=CAPITAL_API_TIMEOUT_SECONDS)
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=20)
            self._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_auth_tokens(self, login: str, password: str, api_key: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Авторизуется и возвращает токены сессии.
        Возвращает (cst, x_security_token, error_message).
        """
        auth_headers = {
            "X-CAP-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        auth_body = {
            "identifier": login,
            "password": password,
            "encryptedPassword": False
        }

        try:
            session = self._get_session()
            async with session.post(f"{self.BASE_URL}/session", json=auth_body, headers=auth_headers) as resp:
                if resp.status == 401:
                    return None, None, "Неверный логин, пароль или API Key."
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Capital auth failed: {resp.status} - {error_text}")
                    return None, None, f"Ошибка API Capital.com (Status: {resp.status})"
                
                cst = resp.headers.get("CST")
                x_sec = resp.headers.get("X-SECURITY-TOKEN")
                
                if not cst or not x_sec:
                    return None, None, "Не получены токены безопасности от Capital.com"
                    
                return cst, x_sec, None
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Capital auth network error: {e}")
            return None, None, "Ошибка соединения с сервером Capital.com."
        except (ValueError, KeyError, OSError) as e:
            logger.error(f"Unexpected Capital auth error: {e}")
            return None, None, "Неожиданная ошибка при подключении к Capital.com."

    async def check_connection(self, login: str, password: str, api_key: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Авторизуется, получает баланс И список позиций.
        Возвращает (data, error_message). Если data есть, error_message = None.
        
        Автоматически повторяет запрос до 3 раз при сетевых ошибках.
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return await self._check_connection_impl(login, password, api_key)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"Capital API attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Capital API failed after {max_retries} attempts: {e}")
                    return None, "Ошибка соединения с сервером Capital.com."
        
        return None, "Неожиданная ошибка при подключении к Capital.com."
    
    async def _check_connection_impl(self, login: str, password: str, api_key: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Внутренняя реализация проверки подключения (без retry).

        Сетевые исключения (aiohttp.ClientError, asyncio.TimeoutError) НЕ ловятся
        здесь намеренно — их должен обработать retry-цикл в `check_connection`.
        Наружу возвращаются только «логические» ошибки (401, 5xx, парсинг).
        """

        # STEP 1: AUTHENTICATION
        auth_headers = {
            "X-CAP-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        auth_body = {
            "identifier": login,
            "password": password,
            "encryptedPassword": False
        }

        session = self._get_session()
        async with session.post(f"{self.BASE_URL}/session", json=auth_body, headers=auth_headers) as resp:
            if resp.status == 401:
                return None, "Неверный логин, пароль или API Key."
            if resp.status != 200:
                error_text = await resp.text()
                logger.error(f"Capital Auth Failed: {resp.status} - {error_text}")
                return None, f"Ошибка API Capital.com (Status: {resp.status})"

            cst = resp.headers.get("CST")
            x_sec = resp.headers.get("X-SECURITY-TOKEN")

            if not cst or not x_sec:
                return None, "Не получены токены безопасности от Capital.com"

        base_headers = {
            "X-CAP-API-KEY": api_key,
            "CST": cst,
            "X-SECURITY-TOKEN": x_sec
        }

        # STEP 2: GET ACCOUNT BALANCE
        account_data = {}
        session = self._get_session()
        async with session.get(f"{self.BASE_URL}/accounts", headers=base_headers) as resp:
            if resp.status == 200:
                try:
                    data = await resp.json()
                    if "accounts" in data and len(data["accounts"]) > 0:
                        main_acc = data["accounts"][0]
                        balance_obj = main_acc.get("balance", {})
                        account_data = {
                            "balance": balance_obj.get("balance", 0.0),
                            "currency": balance_obj.get("currency", "USD"),
                            "available": balance_obj.get("available", 0.0),
                            "account_pnl": balance_obj.get("profitLoss", 0.0), 
                        }
                except (ValueError, KeyError) as e:
                    logger.error(f"Ошибка парсинга баланса: {e}")

        if not account_data:
            return None, "Не удалось получить данные аккаунта."

        # STEP 3: GET OPEN POSITIONS
        positions_summary = {
            "count": 0,
            "total_pnl": 0.0
        }
        
        session = self._get_session()
        async with session.get(f"{self.BASE_URL}/positions", headers=base_headers) as resp:
            if resp.status == 200:
                try:
                    pos_data = await resp.json()
                    positions = pos_data.get("positions", [])
                    
                    positions_summary["count"] = len(positions)
                    positions_summary["total_pnl"] = sum(
                        p.get("position", {}).get("profit", 0.0) for p in positions
                    )
                except (ValueError, KeyError) as e:
                    logger.error(f"Ошибка парсинга позиций: {e}")

        # STEP 4: BUILD RESULT
        result = {
            "balance": account_data["balance"],
            "currency": account_data["currency"],
            "available": account_data["available"],
            "pnl": positions_summary["total_pnl"] if positions_summary["count"] > 0 else account_data["account_pnl"],
            "positions_count": positions_summary["count"],
            "equity": account_data["balance"] + positions_summary["total_pnl"]
        }
        
        return result, None

# GLOBAL CLIENT INSTANCE

capital_client = CapitalClient()