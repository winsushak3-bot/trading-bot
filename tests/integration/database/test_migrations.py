# tests/integration/database/test_migrations.py
"""
Интеграционный тест Alembic-миграций.

Проверяет:
1. Чистая SQLite-база → `alembic upgrade head` проходит без ошибок.
2. Все ожидаемые таблицы созданы.
3. `alembic downgrade base` проходит и удаляет таблицы.

Зачем: если кто-то добавит таблицу в модели, но забудет миграцию, тест покраснеет.

Также покрывает bug fix: `trades.broker_account_id` → `ON DELETE SET NULL`
(ревизия `b3c4d5e6f7a8`). На SQLite это работает через `batch_alter_table`.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect


# ── Paths ────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ALEMBIC_INI = _REPO_ROOT / "alembic.ini"


# ── Фактический список таблиц после `upgrade head` ──
# Должен совпадать с именами `__tablename__` у всех моделей под `shared.database.models`.
# Если добавляете/удаляете модель — обновите этот список И создайте миграцию.
_EXPECTED_TABLES = {
    "users",
    "tickets",
    "ticket_messages",
    "trades",
    "broker_accounts",
    "home_tiles",
}


def _run_alembic(args: list[str], db_url: str) -> subprocess.CompletedProcess:
    """Запускает alembic в subprocess с изолированным окружением.

    Возвращает CompletedProcess. В случае ненулевого exit code — AssertionError
    с полным stderr для быстрого дебага.
    """
    env = os.environ.copy()
    env["ALEMBIC_SQLALCHEMY_URL"] = db_url
    # Форсируем UTF-8 для stdout/stderr на Windows, иначе emoji из docstring'ов
    # миграций ломают подсистему логгера.
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(_ALEMBIC_INI), *args],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise AssertionError(
            f"alembic {' '.join(args)} failed (exit {result.returncode})\n"
            f"── STDOUT ──\n{result.stdout}\n"
            f"── STDERR ──\n{result.stderr}"
        )
    return result


@pytest.fixture
def tmp_sqlite_url(tmp_path: Path) -> tuple[str, str]:
    """Готовит пустой SQLite-файл и возвращает пару (async_url, sync_url).

    Alembic env.py использует `async_engine_from_config` (aiosqlite-драйвер),
    а проверки таблиц в самом тесте делаются синхронным `inspect()`.
    """
    db_file = tmp_path / "migrations_test.db"
    # Пустой файл — чтобы SQLite создал БД на первом коннекте.
    db_file.touch()

    # Путь к файлу — в POSIX-формате для URL, даже на Windows.
    posix_path = db_file.as_posix()
    async_url = f"sqlite+aiosqlite:///{posix_path}"
    sync_url = f"sqlite:///{posix_path}"
    return async_url, sync_url


def _list_tables(sync_url: str) -> set[str]:
    engine = create_engine(sync_url)
    try:
        inspector = inspect(engine)
        return set(inspector.get_table_names())
    finally:
        engine.dispose()


def test_alembic_upgrade_head_creates_all_expected_tables(tmp_sqlite_url) -> None:
    """`alembic upgrade head` на чистой SQLite создаёт все ожидаемые таблицы."""
    async_url, sync_url = tmp_sqlite_url

    # До миграции таблиц нет.
    assert _list_tables(sync_url) == set()

    _run_alembic(["upgrade", "head"], async_url)

    tables = _list_tables(sync_url)

    # alembic_version — служебная таблица Alembic, должна быть всегда.
    assert "alembic_version" in tables, (
        "Alembic должен создать таблицу alembic_version для трекинга ревизий"
    )

    # Все наши доменные таблицы должны присутствовать.
    missing = _EXPECTED_TABLES - tables
    assert not missing, (
        f"После `alembic upgrade head` отсутствуют таблицы: {sorted(missing)}. "
        f"Скорее всего, модель добавлена, но миграция не написана."
    )


def test_alembic_downgrade_base_removes_all_domain_tables(tmp_sqlite_url) -> None:
    """После `alembic upgrade head` → `alembic downgrade base`
    все доменные таблицы должны быть удалены (останется только alembic_version)."""
    async_url, sync_url = tmp_sqlite_url

    _run_alembic(["upgrade", "head"], async_url)
    _run_alembic(["downgrade", "base"], async_url)

    tables = _list_tables(sync_url)

    # После downgrade base — все миграции откачены.
    # alembic_version МОЖЕТ остаться (Alembic сам её не дропает, это нормально).
    leftovers = tables & _EXPECTED_TABLES
    assert not leftovers, (
        f"После `alembic downgrade base` остались незачищенные таблицы: "
        f"{sorted(leftovers)}. Проверьте `downgrade()`-функции миграций."
    )


def test_trades_broker_account_fk_is_set_null_after_upgrade(tmp_sqlite_url) -> None:
    """После `upgrade head` FK `trades.broker_account_id → broker_accounts.id`
    имеет `ON DELETE SET NULL` (регрессия для ревизии b3c4d5e6f7a8)."""
    async_url, sync_url = tmp_sqlite_url
    _run_alembic(["upgrade", "head"], async_url)

    engine = create_engine(sync_url)
    try:
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("trades")
    finally:
        engine.dispose()

    broker_fk = next(
        (fk for fk in fks if fk["referred_table"] == "broker_accounts"),
        None,
    )
    assert broker_fk is not None, (
        "В таблице trades отсутствует FK на broker_accounts — проверьте модель."
    )

    options = broker_fk.get("options") or {}
    assert options.get("ondelete", "").upper() == "SET NULL", (
        f"FK trades.broker_account_id должен иметь ON DELETE SET NULL, "
        f"получено: {options.get('ondelete')!r}. "
        f"Регрессия ревизии b3c4d5e6f7a8_trades_broker_set_null — "
        f"при CASCADE удаление брокера стирает всю историю сделок."
    )
