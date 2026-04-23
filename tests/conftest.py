# tests/conftest.py
"""
Глобальные фикстуры для всех тестов.

ВАЖНО: Этот файл выполняется pytest'ом ДО загрузки любого теста, и первые строки
ниже подгружают `.env.test` ещё ДО того, как будет импортирован `shared.config`.
Это гарантирует, что pydantic-settings увидит переменные окружения из `.env.test`
(они имеют приоритет над `.env` для BaseSettings).
"""
# ──────────────────────────────────────────────────────────────────────────────
# Bootstrap: грузим .env.test ДО любых импортов, зависящих от shared.config.
# Порядок здесь критичен — не переставлять!
# ──────────────────────────────────────────────────────────────────────────────
import os
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TEST_ENV = _REPO_ROOT / ".env.test"
if _TEST_ENV.exists():
    # override=True — перекрываем возможный унаследованный .env из окружения разработчика,
    # чтобы тесты всегда работали на одних и тех же значениях.
    load_dotenv(_TEST_ENV, override=True)
# Явно помечаем режим тестирования — удобно для условной логики в приложении.
os.environ.setdefault("APP_ENV", "test")

# ──────────────────────────────────────────────────────────────────────────────
# Теперь безопасно импортировать модули, читающие конфиг.
# ──────────────────────────────────────────────────────────────────────────────
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from shared.database.models.base import Base


# ============================================================================
# EVENT LOOP
# ============================================================================
# Ранее здесь был кастомный session-scoped `event_loop` fixture — он удалён:
# с `asyncio_mode = auto` (см. pytest.ini) pytest-asyncio 0.21+ сам управляет
# жизненным циклом loop'а, а переопределение вызывает DeprecationWarning
# и ломает корректную работу фикстур "function"-скоупа.


# ============================================================================
# DATABASE
# ============================================================================

@pytest.fixture(scope="function")
async def db_engine():
    """Создает in-memory SQLite engine для каждого теста."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Очищаем после теста
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Создает сессию БД для каждого теста."""
    session_maker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_maker() as session:
        yield session
        await session.rollback()


# ============================================================================
# TEST DATA
# ============================================================================

@pytest.fixture
def test_user_data():
    """Базовые данные тестового пользователя."""
    return {
        "tg_id": 123456789,
        "username": "test_user",
        "language": "ru"
    }


@pytest.fixture
def test_account_data():
    """Базовые данные тестового брокерского аккаунта."""
    return {
        "user_id": 123456789,
        "api_key": "test_api_key_12345",
        "password": "test_password_12345",
        "account_name": "test@example.com"
    }


# ============================================================================
# MOCKS
# ============================================================================

@pytest.fixture
def mock_capital_response_success():
    """Успешный ответ от Capital.com API."""
    return {
        "balance": 10000.0,
        "currency": "USD",
        "available": 9500.0,
        "pnl": 0.0,
        "positions_count": 0,
        "equity": 10000.0
    }


@pytest.fixture
def mock_capital_response_error():
    """Ошибка от Capital.com API."""
    return None, "Неверный логин, пароль или API Key."
