from __future__ import annotations

import hashlib
import hmac
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update
from fastapi import APIRouter, Header, HTTPException, Request

from bot.error_handler import register_error_handler
from bot.setup import build_bot, build_dispatcher, build_storage
from shared.utils.i18n import i18n
from shared.config import config
from shared.lifecycle import shutdown_shared_resources

logger = logging.getLogger(__name__)

router = APIRouter()

_bot: Bot | None = None
_dp: Dispatcher | None = None

WEBHOOK_PATH = "/api/telegram/webhook"


def _compute_webhook_secret() -> str:
    """
    Детерминированный secret_token для Telegram webhook.
    Выводится из BOT_TOKEN: тот, кто знает BOT_TOKEN, может его посчитать,
    но злоумышленник без BOT_TOKEN — нет. Формат: hex SHA-256 (64 символа),
    удовлетворяет требованиям Telegram (A-Z, a-z, 0-9, _, -, 1..256 символов).
    """
    bot_token = config.BOT_TOKEN.get_secret_value()
    return hashlib.sha256(f"webhook-secret:{bot_token}".encode()).hexdigest()


async def startup_bot_webhook() -> None:
    global _bot, _dp

    if _bot is not None and _dp is not None:
        return

    i18n.load_locales()

    storage = await build_storage()
    _bot = build_bot()
    _dp = build_dispatcher(storage)
    register_error_handler(_dp, _bot)

    if config.WEBHOOK_BASE_URL:
        # Normalize user-provided URL from env/bat (trim spaces, trailing slash).
        base_url = config.WEBHOOK_BASE_URL.strip().rstrip("/")
        if not base_url.startswith("https://"):
            logger.warning("WEBHOOK_BASE_URL must start with https://, got: %s", base_url)
            return

        webhook_url = f"{base_url}{WEBHOOK_PATH}"
        webhook_secret = _compute_webhook_secret()
        try:
            await _bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                secret_token=webhook_secret,
            )
            logger.info("Telegram webhook is set to %s (with secret_token)", webhook_url)
        except TelegramBadRequest as e:
            # Do not fail whole API startup when webhook URL is temporarily invalid.
            logger.error("Failed to set Telegram webhook (%s): %s", webhook_url, e)
        except Exception as e:
            logger.error("Unexpected error while setting webhook (%s): %s", webhook_url, e)
    else:
        logger.warning("WEBHOOK_BASE_URL is empty, webhook was not auto-configured")


async def shutdown_bot_webhook() -> None:
    global _bot, _dp

    # Единый shutdown для shared-ресурсов (aiogram-сессия, capital_client,
    # SQLAlchemy engine). См. shared/lifecycle.py.
    await shutdown_shared_resources(bot=_bot)

    _bot = None
    _dp = None


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if _bot is None or _dp is None:
        raise HTTPException(status_code=503, detail="Bot webhook is not initialized")

    # Валидация заголовка: только Telegram, знающий secret_token из set_webhook,
    # может вызывать этот endpoint.
    expected_secret = _compute_webhook_secret()
    if not x_telegram_bot_api_secret_token or not hmac.compare_digest(
        x_telegram_bot_api_secret_token, expected_secret
    ):
        logger.warning("Rejected webhook call: bad or missing secret token")
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    payload = await request.json()
    update = Update.model_validate(payload, context={"bot": _bot})
    await _dp.feed_update(_bot, update)
    return {"ok": True}
