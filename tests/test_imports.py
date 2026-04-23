# tests/test_imports.py
"""
Smoke-тесты импортов ключевых модулей.

Цель: отловить ситуации, когда модуль падает при import-time из-за:
- обращения к конфигу без валидных ENV;
- побочных эффектов на уровне модуля (например, `crypto = CryptoService()`);
- отсутствующих зависимостей.

Эти тесты — "канарейка" для всего проекта: если они красные, значит что-то
в скелете сломалось на уровне загрузки модулей, и остальные тесты даже не
добежали до фикстур.
"""

import importlib

import pytest


# ── Модули, которые должны импортироваться чисто ───────────────────
# Разбиты по подсистемам, чтобы при падении сразу было видно виновника.

_CORE_MODULES = [
    # Shared core
    "shared.config",
    "shared.constants",
    "shared.utils.i18n",
    "shared.database.core",
    "shared.database.models",
    "shared.database.models.base",
    "shared.utils.logger",
    "shared.utils.asyncio_policy",
    # Cryptography — критично, т.к. раньше падал на import из-за
    # module-level `crypto = CryptoService()`.
    "shared.services.cryptography",
    # Repos зависят от crypto и от моделей
    "shared.database.repo.users",
    "shared.database.repo.accounts",
    "shared.database.repo.support",
]

_BOT_MODULES = [
    "bot.main",
    "bot.setup",
    "bot.states",
    "bot.middlewares.db",
    "bot.middlewares.i18n",
    "bot.middlewares.outer",
    "bot.middlewares.throttling",
    "bot.handlers.common.start",
    "bot.handlers.common.onboarding",
    "bot.handlers.common.back",
    "bot.handlers.profile",
    "bot.handlers.admin.panel",
]

_BACKEND_MODULES = [
    "backend.main",
    "backend.bot_webhook",
    "backend.core.deps",
    "backend.core.database",
    "backend.api.routes.auth",
    "backend.api.routes.admin_auth",
    "backend.api.routes.trading",
    "backend.api.routes.support",
    "backend.api.routes.home",
    "backend.api.routes.news",
    "backend.api.routes.charts",
    "backend.api.routes.uploads",
    "backend.services.news",
]


@pytest.mark.parametrize("module_name", _CORE_MODULES)
def test_core_module_imports(module_name: str) -> None:
    """Core shared-модули должны импортироваться без ошибок при .env.test."""
    importlib.import_module(module_name)


@pytest.mark.parametrize("module_name", _BOT_MODULES)
def test_bot_module_imports(module_name: str) -> None:
    """Bot-модули должны импортироваться без запуска polling."""
    importlib.import_module(module_name)


@pytest.mark.parametrize("module_name", _BACKEND_MODULES)
def test_backend_module_imports(module_name: str) -> None:
    """FastAPI backend-модули должны импортироваться без старта сервера."""
    importlib.import_module(module_name)


def test_config_loaded_from_env_test() -> None:
    """Убеждаемся, что conftest.py действительно подгрузил .env.test,
    а не случайно подтянутый dev-`.env` разработчика."""
    from shared.config import config

    # Значения ровно из .env.test — маркеры того, что bootstrap сработал.
    assert config.DB_URL == "sqlite+aiosqlite:///:memory:", (
        "DB_URL должен быть in-memory SQLite из .env.test — "
        "иначе conftest.py не загрузил тестовое окружение"
    )
    assert 123456789 in config.ADMIN_IDS, (
        "ADMIN_IDS должен содержать тестовый ID 123456789 из .env.test"
    )


def test_crypto_is_lazy_singleton() -> None:
    """Проверяем, что module-level `crypto` не инициализируется
    на import-time, а только при первом обращении (PEP 562 __getattr__)."""
    import shared.services.cryptography as crypto_mod

    # До обращения к `crypto` singleton должен быть None.
    crypto_mod.reset_crypto_for_tests()
    assert crypto_mod._crypto_singleton is None

    # Первое обращение — создаёт инстанс.
    _ = crypto_mod.crypto
    assert crypto_mod._crypto_singleton is not None

    # Повторное обращение — возвращает тот же инстанс (singleton).
    assert crypto_mod.crypto is crypto_mod._crypto_singleton


def test_crypto_roundtrip_with_test_fernet_key() -> None:
    """Сквозной тест: с валидным Fernet-ключом из .env.test
    шифрование / расшифровка работают."""
    from shared.services.cryptography import crypto

    secret = "api_key_roundtrip_check"
    token = crypto.encrypt(secret)
    assert token and token != secret
    assert crypto.decrypt(token) == secret
