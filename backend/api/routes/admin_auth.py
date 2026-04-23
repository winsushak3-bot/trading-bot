"""
Admin auth endpoints — login по Telegram ID + паролю (только для /admin UI).

Возвращает подписанный admin token, который фронт отдаёт как
`Authorization: Admin <token>` во всех admin API запросах.
"""

import hmac
import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.core.security import create_admin_token
from shared.config import config

router = APIRouter()

_TOKEN_TTL_SECONDS = 24 * 60 * 60
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 60
_login_attempts: dict[str, list[float]] = defaultdict(list)
_last_cleanup: float = 0.0
_CLEANUP_INTERVAL = 300  # очистка каждые 5 минут


class AdminLoginRequest(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id администратора")
    password: str = Field(..., min_length=1)


class AdminLoginResponse(BaseModel):
    token: str
    expires_in: int


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest, request: Request) -> AdminLoginResponse:
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()

    # Периодическая очистка всех устаревших записей (защита от memory leak)
    global _last_cleanup
    if now - _last_cleanup > _CLEANUP_INTERVAL:
        stale_keys = [k for k, v in _login_attempts.items() if all(now - t >= _WINDOW_SECONDS for t in v)]
        for k in stale_keys:
            del _login_attempts[k]
        _last_cleanup = now

    attempts = _login_attempts[client_ip]
    _login_attempts[client_ip] = [t for t in attempts if now - t < _WINDOW_SECONDS]
    if len(_login_attempts[client_ip]) >= _MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many login attempts, try later")
    _login_attempts[client_ip].append(now)

    if config.ADMIN_PASSWORD is None:
        raise HTTPException(status_code=503, detail="Admin login is not configured on server")

    if payload.telegram_id not in config.ADMIN_IDS:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not hmac.compare_digest(payload.password, config.ADMIN_PASSWORD.get_secret_value()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_admin_token(payload.telegram_id, ttl_seconds=_TOKEN_TTL_SECONDS)
    return AdminLoginResponse(token=token, expires_in=_TOKEN_TTL_SECONDS)
