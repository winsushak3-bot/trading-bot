"""Charts API — OHLCV data for crypto (Binance) and forex (Capital.com).

Эндпоинты требуют Telegram WebApp initData: без авторизации любой внешний
клиент мог бы расходовать наш rate-limit на Binance/Capital.

Реализация вынесена в `backend.core.market_data`.
"""

from fastapi import APIRouter, Depends, HTTPException

from backend.core.deps import get_current_user_id
from backend.core.market_data import (
    MarketDataError,
    fetch_binance_ohlcv,
    fetch_capital_ohlcv,
)

router = APIRouter()


@router.get("/crypto/ohlcv/{symbol:path}")
async def crypto_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 300,
    since: int | None = None,
    _user_id: int = Depends(get_current_user_id),
):
    """Fetch OHLCV from Binance Futures (public, no key needed)."""
    try:
        candles = await fetch_binance_ohlcv(symbol, timeframe, limit=limit, since=since)
    except MarketDataError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"symbol": symbol.upper(), "timeframe": timeframe, "candles": candles}


@router.get("/forex/ohlcv/{symbol}")
async def forex_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 300,
    _user_id: int = Depends(get_current_user_id),
):
    """Fetch OHLCV from Capital.com (uses project credentials, cached session)."""
    try:
        candles = await fetch_capital_ohlcv(symbol, timeframe, limit=limit)
    except MarketDataError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"symbol": symbol.upper(), "timeframe": timeframe, "candles": candles}
