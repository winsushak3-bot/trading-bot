# shared/lifecycle.py
"""
Единый shutdown-лайфсайкл для всех точек входа проекта
(`bot/main.py`, `backend/main.py`).

Цель: один источник истины по закрытию shared-ресурсов, чтобы:
  * не забыть закрыть HTTP-сессию Capital.com, когда добавим новую точку входа;
  * не было гонок shutdown между bot + backend в webhook-режиме;
  * каждый ресурс закрывался с таймаутом и индивидуальным try/except —
    отказ одного не мешал закрывать остальные.

Использование:
    from shared.lifecycle import shutdown_shared_resources
    await shutdown_shared_resources(bot=bot)  # bot опциональный

Если в проекте появится новый shared-ресурс (например, Bybit-клиент),
добавляйте его сюда, а не в каждую точку входа.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


# Глобальный таймаут на любое одно закрытие — чтобы зависшая сессия
# (например, мёртвый TCP connection) не блокировала shutdown всего процесса.
_CLOSE_TIMEOUT_SECONDS = 5.0


async def _close_with_timeout(name: str, coro: Any) -> None:
    """Ожидаемый тип coro: awaitable. Закрывает ресурс, ловит ВСЕ исключения,
    применяет таймаут. Не падает — только логирует."""
    try:
        await asyncio.wait_for(coro, timeout=_CLOSE_TIMEOUT_SECONDS)
        logger.info("✅ Shutdown: %s закрыт", name)
    except asyncio.TimeoutError:
        logger.warning("⚠️  Shutdown: %s не закрылся за %.1fs — пропускаем",
                       name, _CLOSE_TIMEOUT_SECONDS)
    except Exception as e:  # noqa: BLE001 — здесь намеренно глотаем всё
        logger.warning("⚠️  Shutdown: при закрытии %s: %s", name, e)


async def shutdown_shared_resources(bot: Any | None = None) -> None:
    """Корректно закрывает общие ресурсы проекта.

    Args:
        bot: опционально — инстанс `aiogram.Bot`. Если передан, его
             `bot.session` будет закрыт. `None` означает, что бот не
             использовался в этой точке входа (например, чистый backend).

    Безопасно вызывать несколько раз — каждый ресурс закрывается с try/except,
    повторное закрытие тоже обработано корректно (закрытые сессии не падают).
    """
    logger.info("🔄 Shutdown: закрытие общих ресурсов...")

    # ── 1. aiogram Bot session (HTTP к Telegram API) ──
    if bot is not None:
        session = getattr(bot, "session", None)
        if session is not None:
            await _close_with_timeout("aiogram.Bot.session", session.close())

    # ── 2. Capital.com HTTP session (shared client) ──
    # Ленивый импорт, чтобы не тянуть Capital-зависимости, если shutdown
    # вызывается в контексте, где Capital не использовался (например, в тестах).
    try:
        from shared.services.capital import capital_client
        await _close_with_timeout("capital_client", capital_client.close())
    except Exception as e:  # noqa: BLE001
        logger.debug("shutdown: capital_client импорт/закрытие: %s", e)

    # ── 3. SQLAlchemy engine pool ──
    try:
        from shared.database.core import engine
        await _close_with_timeout("SQLAlchemy engine", engine.dispose())
    except Exception as e:  # noqa: BLE001
        logger.debug("shutdown: engine.dispose: %s", e)

    logger.info("✅ Shutdown: все shared-ресурсы закрыты")
