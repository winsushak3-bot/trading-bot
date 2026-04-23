# bot/main.py

# IMPORTS

import asyncio
from aiogram.types import BotCommandScopeChat, BotCommandScopeAllGroupChats, BotCommandScopeDefault

from shared.config import config
from shared.utils.asyncio_policy import apply_windows_event_loop_policy
from shared.utils.logger import setup_logger
from shared.lifecycle import shutdown_shared_resources
from bot.error_handler import register_error_handler
from bot.setup import build_bot, build_dispatcher, build_storage
from shared.utils.i18n import i18n

# LOGGER SETUP

logger = setup_logger()

# MAIN FUNCTION

async def main():
    logger.info("🚀 Запуск бота (polling-режим)...")

    # ── MODE DETECTION: POLLING vs WEBHOOK ────────────────────────
    #
    # Бот может получать апдейты ОДНИМ из двух способов:
    #   1) polling — сам бот (этот файл) опрашивает Telegram каждую секунду.
    #      Нужен, когда нет публичного HTTPS-URL (локалка без ngrok).
    #   2) webhook — Telegram шлёт апдейты на FastAPI-endpoint в `backend`.
    #      Включается автоматически, если задан `WEBHOOK_BASE_URL` в `.env`.
    #
    # ОБА режима одновременно запускать НЕЛЬЗЯ — Telegram обслуживает бота
    # только одним источником апдейтов, и каждый `getUpdates`/`setWebhook`
    # перебивает другой (гонка «кто последний зарегистрировался — тот
    # получает апдейты»). Поэтому если webhook настроен, polling-точка
    # входа должна тихо выйти, а не запускать свой `start_polling`.
    #
    # Это делает `start-wt.bat` безопасным при любой конфигурации: запускаем
    # оба процесса, но фактически активен только один из режимов.
    if config.WEBHOOK_BASE_URL and config.WEBHOOK_BASE_URL.strip():
        logger.warning(
            "⏭️  WEBHOOK_BASE_URL задан в .env — polling отключён, чтобы не "
            "конфликтовать с webhook-режимом в backend. "
            "Обновления Telegram принимает `backend.bot_webhook` (FastAPI)."
        )
        logger.info("👋 bot.main завершён без запуска polling (webhook активен).")
        return

    # ENVIRONMENT VALIDATION
    #
    # Основная валидация ENV (ENCRYPTION_KEY как Fernet-ключ, DB_URL диалект,
    # REDIS_URL схема) уже выполнена на уровне `Settings`-модели в
    # `shared/config.py` — если мы сюда дошли, значит pydantic уже прогнал
    # все `field_validator`'ы и поднял осмысленные ValidationError для битых
    # значений. Здесь остаются только бизнес-проверки «не пусто».
    logger.info("🔍 Проверка переменных окружения...")

    if not config.BOT_TOKEN.get_secret_value():
        raise ValueError("BOT_TOKEN не может быть пустым")
    if not config.ADMIN_IDS:
        raise ValueError("ADMIN_IDS должен содержать хотя бы один ID")

    logger.info("✅ Переменные окружения валидны (Fernet-ключ, DB_URL, REDIS_URL)")

    # I18N INITIALIZATION
    i18n.load_locales()

    # DATABASE SCHEMA
    #
    # Единственный источник истины для схемы — Alembic-миграции:
    #   alembic upgrade head
    #
    # Ранее здесь был `Base.metadata.create_all(...)` — это создавало таблицы
    # в обход миграций и не записывало версию в `alembic_version`, из-за чего
    # последующий `alembic upgrade head` падал с «таблица уже существует».
    # Убрано. Бот теперь ожидает, что миграции уже применены на DB_URL.
    logger.info("📦 Схема БД — из Alembic. Не забудьте `alembic upgrade head` перед запуском.")

    # STORAGE / BOT / DISPATCHER SETUP (unified via bot.setup)
    storage = await build_storage()
    bot = build_bot()
    dp = build_dispatcher(storage)

    # GLOBAL ERROR HANDLER (shared with webhook mode)
    register_error_handler(dp, bot)

    # CLEAR COMMAND MENU (removes / suggestions in all chats)
    scopes = [
        BotCommandScopeAllGroupChats(),
        BotCommandScopeDefault(),
    ]
    if config.CHANNEL_ID:
        scopes.append(BotCommandScopeChat(chat_id=config.CHANNEL_ID))
    for scope in scopes:
        try:
            await bot.delete_my_commands(scope=scope)
        except Exception as e:
            logger.warning(f"⚠️ Could not clear command menu for {scope}: {e}")
    logger.info("✅ Command menu cleanup done")

    # START POLLING
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info("✅ Бот запущен и готов к работе")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.info("⏸️ Получен сигнал остановки...")
    finally:
        # Единый shutdown для всех shared-ресурсов (см. shared/lifecycle.py).
        await shutdown_shared_resources(bot=bot)
        logger.info("✅ Бот остановлен корректно")

# ENTRY POINT

if __name__ == "__main__":
    apply_windows_event_loop_policy()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Бот выключен")
