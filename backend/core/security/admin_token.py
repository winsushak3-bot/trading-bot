"""
Signed admin session tokens.

Используется когда /admin UI открывается из браузера (не как Telegram WebApp),
поэтому Telegram initData недоступен и нужен отдельный механизм аутентификации.

Формат токена: <base64url(payload_json)>.<hex(hmac_sha256(payload_json, BOT_TOKEN))>
payload = {"uid": <telegram_id>, "exp": <unix_ts>}

HMAC подписывается BOT_TOKEN'ом — тем же секретом что используется для webhook.
Ключ никогда не попадает на клиент; клиент только хранит и отдаёт готовый токен.
"""

from __future__ import annotations

import base64
import hmac
import hashlib
import json
import time
from typing import Optional

from shared.config import config


DEFAULT_TTL_SECONDS = 24 * 60 * 60  # 24 часа


def _sign(payload_bytes: bytes) -> str:
    secret = config.BOT_TOKEN.get_secret_value().encode("utf-8")
    return hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def create_admin_token(user_id: int, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
    """Создаёт подписанный токен для админа с заданным TTL."""
    payload = {"uid": int(user_id), "exp": int(time.time()) + int(ttl_seconds)}
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = _b64url_encode(payload_bytes)
    signature = _sign(payload_bytes)
    return f"{payload_b64}.{signature}"


def verify_admin_token(token: str) -> Optional[int]:
    """
    Проверяет подпись и срок действия токена. Возвращает user_id или None если невалиден.
    """
    if not token or "." not in token:
        return None
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError:
        return None

    try:
        payload_bytes = _b64url_decode(payload_b64)
    except (ValueError, TypeError):
        return None

    expected_signature = _sign(payload_bytes)
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None

    exp = payload.get("exp")
    uid = payload.get("uid")
    if not isinstance(exp, int) or not isinstance(uid, int):
        return None
    if exp < int(time.time()):
        return None

    return uid
