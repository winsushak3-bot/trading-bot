"""
Unit-тесты для `backend.core.market_data`:
  * `get_capital_session` — кеширует CST на TTL, защищает от race condition.
  * `fetch_binance_ohlcv` парсер — проверяет форму ответа на мок-данных.

Мы не ходим в реальные Binance/Capital — везде мокируем `aiohttp`.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core import market_data as md
from backend.core.market_data import (
    MarketDataError,
    binance_timeframe,
    capital_timeframe,
    get_capital_session,
    invalidate_capital_session,
    normalize_binance_symbol,
)


# ── normalize / timeframe helpers ─────────────────────────────

def test_normalize_binance_symbol():
    assert normalize_binance_symbol("btc/usdt") == "BTCUSDT"
    assert normalize_binance_symbol("eth-usdt") == "ETHUSDT"
    assert normalize_binance_symbol("SOLUSDT") == "SOLUSDT"


def test_binance_timeframe_ok():
    assert binance_timeframe("5m") == "5m"
    assert binance_timeframe("1h") == "1h"


def test_binance_timeframe_invalid():
    with pytest.raises(MarketDataError, match="Invalid timeframe"):
        binance_timeframe("42s")


def test_capital_timeframe_ok():
    assert capital_timeframe("5m") == "MINUTE_5"
    assert capital_timeframe("1h") == "HOUR"


def test_capital_timeframe_invalid():
    with pytest.raises(MarketDataError, match="Invalid timeframe"):
        capital_timeframe("3m")


# ── Capital session cache ─────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_capital_cache():
    invalidate_capital_session()
    yield
    invalidate_capital_session()


@pytest.mark.asyncio
async def test_capital_session_caches_within_ttl():
    """Повторные вызовы в рамках TTL должны использовать кеш (1 реальная авторизация)."""
    fake_get_tokens = AsyncMock(return_value=("CST-1", "SEC-1", None))
    with patch.object(md.capital_client, "get_auth_tokens", fake_get_tokens):
        r1 = await get_capital_session()
        r2 = await get_capital_session()
        r3 = await get_capital_session()

    assert r1 == r2 == r3 == ("CST-1", "SEC-1")
    fake_get_tokens.assert_awaited_once()


@pytest.mark.asyncio
async def test_capital_session_refetches_after_invalidate():
    fake_get_tokens = AsyncMock(side_effect=[
        ("CST-1", "SEC-1", None),
        ("CST-2", "SEC-2", None),
    ])
    with patch.object(md.capital_client, "get_auth_tokens", fake_get_tokens):
        cst1, _ = await get_capital_session()
        invalidate_capital_session()
        cst2, _ = await get_capital_session()

    assert cst1 == "CST-1"
    assert cst2 == "CST-2"
    assert fake_get_tokens.await_count == 2


@pytest.mark.asyncio
async def test_capital_session_raises_on_auth_error():
    fake_get_tokens = AsyncMock(return_value=(None, None, "bad-credentials"))
    with patch.object(md.capital_client, "get_auth_tokens", fake_get_tokens):
        with pytest.raises(MarketDataError, match="bad-credentials"):
            await get_capital_session()


@pytest.mark.asyncio
async def test_capital_session_no_concurrent_auth():
    """При конкурентных вызовах должна быть РОВНО одна реальная авторизация."""
    call_count = 0

    async def slow_auth(**_kwargs):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return "CST-X", "SEC-X", None

    with patch.object(md.capital_client, "get_auth_tokens", slow_auth):
        results = await asyncio.gather(*(get_capital_session() for _ in range(5)))

    assert all(r == ("CST-X", "SEC-X") for r in results)
    assert call_count == 1, f"ожидали 1 авторизацию, получили {call_count}"


# ── Binance fetchers: мокаем aiohttp.ClientSession ────────────

def _fake_aiohttp_session(response_json, status: int = 200):
    """Возвращает объект-заглушку, имитирующий `async with aiohttp.ClientSession() as s`."""
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=response_json)
    resp.text = AsyncMock(return_value=str(response_json))

    class _FakeReqCtx:
        async def __aenter__(self):
            return resp

        async def __aexit__(self, *a):
            return None

    class _FakeSession:
        def get(self, url, params=None, headers=None):
            return _FakeReqCtx()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

    return _FakeSession()


@pytest.mark.asyncio
async def test_fetch_binance_ohlcv_parses_klines():
    raw = [
        [1_700_000_000_000, "42000", "42100", "41950", "42050", "1.5",
         1_700_000_059_999, "63075", 5, "0.8", "33630", "0"],
        [1_700_000_060_000, "42050", "42080", "42000", "42030", "0.9",
         1_700_000_119_999, "37827", 3, "0.5", "21015", "0"],
    ]
    fake = _fake_aiohttp_session(raw)
    with patch("backend.core.market_data.aiohttp.ClientSession", return_value=fake):
        candles = await md.fetch_binance_ohlcv("BTCUSDT", "1m", limit=2)

    assert len(candles) == 2
    assert candles[0] == {
        "time": 1_700_000_000,
        "open": 42000.0,
        "high": 42100.0,
        "low": 41950.0,
        "close": 42050.0,
        "volume": 1.5,
    }


@pytest.mark.asyncio
async def test_fetch_binance_ohlcv_raises_on_error_status():
    fake = _fake_aiohttp_session({"code": -1}, status=500)
    with patch("backend.core.market_data.aiohttp.ClientSession", return_value=fake):
        with pytest.raises(MarketDataError, match="HTTP 500"):
            await md.fetch_binance_ohlcv("BTCUSDT", "1m")


@pytest.mark.asyncio
async def test_fetch_binance_ohlcv_rejects_invalid_timeframe():
    with pytest.raises(MarketDataError, match="Invalid timeframe"):
        await md.fetch_binance_ohlcv("BTCUSDT", "42s")
