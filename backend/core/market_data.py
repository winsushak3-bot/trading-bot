"""Market-data helpers для backend routes (`charts`).

Что здесь:
  1. `get_capital_session()` — кеш CST/X-SECURITY-TOKEN Capital.com. Токены
     живут ~10 минут, мы кешируем на 9 минут, чтобы не авторизовываться на
     каждом запросе OHLCV.
  2. Fetchers для Binance Futures (public) и Capital.com:
       * `fetch_binance_ohlcv`
       * `fetch_capital_ohlcv`

Все fetchers возвращают единообразные Python-структуры и бросают
`MarketDataError` на HTTP-ошибках провайдера. Роуты уже переводят их в
`HTTPException(502, ...)`.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp

from shared.config import config
from shared.constants import CAPITAL_BASE_URL
from shared.services.capital import capital_client

logger = logging.getLogger(__name__)


# ── Errors ───────────────────────────────────────────────────

class MarketDataError(RuntimeError):
    """HTTP/API error bubbled up from Binance или Capital.com."""


# ── Binance Futures public API ──────────────────────────────

BINANCE_API = "https://fapi.binance.com"

_BINANCE_TF = {
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w",
}


def normalize_binance_symbol(symbol: str) -> str:
    """`btc/usdt` → `BTCUSDT`."""
    return symbol.replace("/", "").replace("-", "").upper()


def binance_timeframe(tf: str) -> str:
    """Валидирует и возвращает TF, иначе бросает `MarketDataError`."""
    resolved = _BINANCE_TF.get(tf)
    if resolved is None:
        raise MarketDataError(
            f"Invalid timeframe '{tf}'. Use: {list(_BINANCE_TF.keys())}"
        )
    return resolved


async def _binance_get(session: aiohttp.ClientSession, path: str, params: dict) -> Any:
    url = f"{BINANCE_API}{path}"
    async with session.get(url, params=params) as resp:
        text = await resp.text()
        if resp.status != 200:
            raise MarketDataError(f"Binance {path} HTTP {resp.status}: {text}")
        try:
            return await resp.json(content_type=None)
        except Exception:
            # На случай, если Binance вдруг вернёт не-JSON (rate-limit page, etc.)
            raise MarketDataError(f"Binance {path}: invalid JSON: {text[:200]}")


async def fetch_binance_ohlcv(
    symbol: str, timeframe: str, limit: int = 500, since: int | None = None,
) -> list[dict]:
    """OHLCV c Binance Futures. `since` — unix millis нижней границы."""
    sym = normalize_binance_symbol(symbol)
    interval = binance_timeframe(timeframe)
    limit = max(1, min(limit, 1500))

    params: dict[str, Any] = {"symbol": sym, "interval": interval, "limit": limit}
    if since is not None:
        params["startTime"] = int(since)

    async with aiohttp.ClientSession() as s:
        raw = await _binance_get(s, "/fapi/v1/klines", params)

    return [
        {
            "time": int(c[0] / 1000),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        }
        for c in raw
    ]


# ── Capital.com (forex) with session cache ───────────────────

_CAPITAL_TF = {
    "1m": "MINUTE", "5m": "MINUTE_5", "15m": "MINUTE_15",
    "30m": "MINUTE_30", "1h": "HOUR", "4h": "HOUR_4", "1d": "DAY", "1w": "WEEK",
}


def capital_timeframe(tf: str) -> str:
    resolved = _CAPITAL_TF.get(tf)
    if resolved is None:
        raise MarketDataError(
            f"Invalid timeframe '{tf}'. Use: {list(_CAPITAL_TF.keys())}"
        )
    return resolved


@dataclass
class _CapitalTokens:
    cst: str
    security_token: str
    expires_at: float  # unix seconds


# Capital session tokens expire в ~10 минут; кешируем на 9, чтобы был запас.
_CAPITAL_TTL_SECONDS = 9 * 60
_capital_cache: _CapitalTokens | None = None
_capital_lock = asyncio.Lock()


async def get_capital_session() -> tuple[str, str]:
    """Возвращает свежую пару (CST, X-SECURITY-TOKEN) с Capital.com.

    Результат кешируется на 9 минут. Конкурентные вызовы не плодят
    параллельные `/session` запросы благодаря `_capital_lock`.

    Это фикс E3 из аудита: раньше каждый запрос OHLCV выполнял отдельную
    авторизацию, что сжирало минутный rate-limit при частых запросах.
    """
    global _capital_cache
    now = time.time()

    cached = _capital_cache
    if cached is not None and cached.expires_at > now:
        return cached.cst, cached.security_token

    async with _capital_lock:
        # Пере-проверяем после lock: пока ждали, другой корутин мог обновить кеш.
        cached = _capital_cache
        if cached is not None and cached.expires_at > time.time():
            return cached.cst, cached.security_token

        cst, sec, error = await capital_client.get_auth_tokens(
            login=config.CAPITAL_EMAIL,
            password=config.CAPITAL_PASSWORD.get_secret_value(),
            api_key=config.CAPITAL_API_KEY.get_secret_value(),
        )
        if error or not cst or not sec:
            raise MarketDataError(f"Capital.com auth failed: {error or 'empty tokens'}")

        _capital_cache = _CapitalTokens(
            cst=cst,
            security_token=sec,
            expires_at=time.time() + _CAPITAL_TTL_SECONDS,
        )
        logger.info("Capital session cached (TTL=%ds)", _CAPITAL_TTL_SECONDS)
        return cst, sec


def invalidate_capital_session() -> None:
    """Сбросить кеш — использовать, если Capital вернул 401 (токен истёк раньше TTL)."""
    global _capital_cache
    _capital_cache = None


async def _capital_get(path: str, params: dict | None = None) -> Any:
    """GET к Capital.com REST API с авто-ретраем при 401 (токен истёк)."""
    from shared.config import config as _cfg
    api_key = _cfg.CAPITAL_API_KEY.get_secret_value()

    for attempt in (1, 2):
        cst, sec = await get_capital_session()
        headers = {"X-CAP-API-KEY": api_key, "CST": cst, "X-SECURITY-TOKEN": sec}
        url = f"{CAPITAL_BASE_URL}{path}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, headers=headers) as resp:
                text = await resp.text()
                if resp.status == 401 and attempt == 1:
                    # Токен мог истечь раньше TTL — сбрасываем и ретраим.
                    logger.warning("Capital 401 on %s, invalidating session and retrying", path)
                    invalidate_capital_session()
                    continue
                if resp.status != 200:
                    raise MarketDataError(f"Capital {path} HTTP {resp.status}: {text}")
                try:
                    return await resp.json(content_type=None)
                except Exception:
                    raise MarketDataError(f"Capital {path}: invalid JSON: {text[:200]}")

    raise MarketDataError(f"Capital {path}: unexpected state after retry")


def _mid(p: dict) -> float:
    """Среднее bid/ask — Capital возвращает цены как {'bid':..., 'ask':...}."""
    return (float(p["bid"]) + float(p["ask"])) / 2.0


async def fetch_capital_ohlcv(
    symbol: str, timeframe: str, limit: int = 300,
) -> list[dict]:
    resolution = capital_timeframe(timeframe)
    limit = max(1, min(limit, 1000))
    data = await _capital_get(
        f"/prices/{symbol.upper()}",
        {"resolution": resolution, "max": limit},
    )
    candles: list[dict] = []
    for p in data.get("prices", []):
        candles.append({
            "time": int(datetime.fromisoformat(
                p["snapshotTime"].replace("Z", "+00:00")
            ).timestamp()),
            "open": _mid(p["openPrice"]),
            "high": _mid(p["highPrice"]),
            "low": _mid(p["lowPrice"]),
            "close": _mid(p["closePrice"]),
            "volume": float(p.get("lastTradedVolume") or 0),
        })
    return candles


