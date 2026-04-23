# tests/unit/test_bot_mode.py
"""
Регрессионные тесты Phase 2: polling/webhook автовыбор и единый shutdown.

Что покрываем:
  1. `bot.main.main()` при заданном WEBHOOK_BASE_URL:
     - НЕ вызывает `build_bot` / `build_dispatcher` / `start_polling`;
     - просто логгирует и возвращается → нет конфликта с backend-webhook.
  2. `bot.main.main()` при пустом WEBHOOK_BASE_URL:
     - валидирует ENV и пытается стартовать polling (мы прерываем на
       `build_storage`, чтобы не лезть в реальный Redis).
  3. `shared.lifecycle.shutdown_shared_resources`:
     - корректно закрывает все три ресурса (bot.session, capital_client,
       engine.dispose) даже если один упадёт;
     - применяет таймаут;
     - безопасен при bot=None.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Phase 2 test #1: webhook mode — bot.main тихо выходит ─────────

@pytest.mark.asyncio
async def test_bot_main_skips_polling_when_webhook_configured(monkeypatch) -> None:
    """Если WEBHOOK_BASE_URL задан — bot.main НЕ должен запускать polling."""
    # Подменяем конфиг ДО импорта bot.main — точнее его значение на момент main().
    from shared.config import config
    monkeypatch.setattr(
        config, "WEBHOOK_BASE_URL", "https://example.ngrok-free.dev",
    )

    # Гарантируем, что никакой build_* / start_polling не будут вызваны.
    from bot import main as bot_main

    with (
        patch.object(bot_main, "build_storage", new_callable=AsyncMock) as m_storage,
        patch.object(bot_main, "build_bot") as m_build_bot,
        patch.object(bot_main, "build_dispatcher") as m_build_dp,
    ):
        # main() должна вернуться без исключений и без вызова build_*
        await bot_main.main()

    m_storage.assert_not_called()
    m_build_bot.assert_not_called()
    m_build_dp.assert_not_called()


@pytest.mark.asyncio
async def test_bot_main_skips_polling_when_webhook_is_empty_string(monkeypatch) -> None:
    """Пустая строка / пробелы в WEBHOOK_BASE_URL НЕ должны считаться
    как 'webhook настроен' — polling должен работать."""
    from shared.config import config
    # Пустая строка ДОЛЖНА интерпретироваться как 'не задан'.
    monkeypatch.setattr(config, "WEBHOOK_BASE_URL", "   ")

    from bot import main as bot_main

    # Прерываем исполнение на build_storage — достаточно, чтобы убедиться,
    # что early-return НЕ сработал.
    with patch.object(bot_main, "build_storage", new_callable=AsyncMock) as m_storage:
        m_storage.side_effect = RuntimeError("stop-here")

        with pytest.raises(RuntimeError, match="stop-here"):
            await bot_main.main()

    # build_storage был вызван — значит главная функция пошла дальше
    # проверки WEBHOOK_BASE_URL и начала собирать polling-инфраструктуру.
    m_storage.assert_called_once()


# ── Phase 2 test #2: shutdown_shared_resources корректность ─────────

@pytest.mark.asyncio
async def test_shutdown_closes_all_resources_in_order() -> None:
    """shutdown_shared_resources закрывает bot.session, capital_client, engine."""
    from shared import lifecycle

    fake_bot = MagicMock()
    fake_bot.session = MagicMock()
    fake_bot.session.close = AsyncMock()

    fake_capital = AsyncMock()
    fake_engine = AsyncMock()

    with (
        patch("shared.services.capital.capital_client", fake_capital),
        patch("shared.database.core.engine", fake_engine),
    ):
        await lifecycle.shutdown_shared_resources(bot=fake_bot)

    fake_bot.session.close.assert_awaited_once()
    fake_capital.close.assert_awaited_once()
    fake_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_shutdown_is_safe_when_bot_is_none() -> None:
    """Если bot=None — shutdown не должен падать на отсутствующем bot.session."""
    from shared import lifecycle

    # Должен просто закрыть capital_client + engine, без bot-шага.
    await lifecycle.shutdown_shared_resources(bot=None)


@pytest.mark.asyncio
async def test_shutdown_continues_if_one_resource_fails() -> None:
    """Если один ресурс упадёт — shutdown должен продолжить закрывать остальные."""
    from shared import lifecycle

    fake_bot = MagicMock()
    fake_bot.session = MagicMock()
    fake_bot.session.close = AsyncMock(side_effect=RuntimeError("bot session boom"))

    fake_capital = AsyncMock()
    fake_engine = AsyncMock()

    with (
        patch("shared.services.capital.capital_client", fake_capital),
        patch("shared.database.core.engine", fake_engine),
    ):
        # Не должно бросить исключение наружу.
        await lifecycle.shutdown_shared_resources(bot=fake_bot)

    # Несмотря на ошибку в bot.session.close, остальные были закрыты.
    fake_capital.close.assert_awaited_once()
    fake_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_shutdown_applies_timeout_to_hung_resource() -> None:
    """Если ресурс висит дольше _CLOSE_TIMEOUT_SECONDS — shutdown не блокируется."""
    from shared import lifecycle

    # Патчим таймаут на короткий, чтобы тест был быстрым.
    monkey_timeout = 0.1

    async def hung_close():
        await asyncio.sleep(10)  # имитация зависшей сессии

    fake_bot = MagicMock()
    fake_bot.session = MagicMock()
    fake_bot.session.close = hung_close

    fake_capital = AsyncMock()
    fake_engine = AsyncMock()

    with (
        patch.object(lifecycle, "_CLOSE_TIMEOUT_SECONDS", monkey_timeout),
        patch("shared.services.capital.capital_client", fake_capital),
        patch("shared.database.core.engine", fake_engine),
    ):
        start = asyncio.get_event_loop().time()
        await lifecycle.shutdown_shared_resources(bot=fake_bot)
        elapsed = asyncio.get_event_loop().time() - start

    # Должно уложиться заметно быстрее, чем 10 сек «зависания».
    assert elapsed < 3.0, f"shutdown висел {elapsed:.1f}s — таймаут не сработал"
    # Остальные ресурсы всё равно закрыты.
    fake_capital.close.assert_awaited_once()
    fake_engine.dispose.assert_awaited_once()
