# database/migrations/env.py
"""
Alembic env configuration for async migrations.

Стандартный env.py с небольшим фиксами под Windows и asyncpg.
"""
import asyncio
import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Путь до проекта должен быть добавлен ДО импортов из shared/*, иначе
# Alembic (запущенный как отдельный процесс) их не найдёт.
sys.path.append(os.getcwd())

# --- FIX FOR WINDOWS & ASYNCPG ---
# Лечит WinError 64 / ConnectionResetError при asyncpg на Windows
from shared.utils.asyncio_policy import apply_windows_event_loop_policy
apply_windows_event_loop_policy()
# ---------------------------------

from shared.config import config as app_config
from shared.database.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

configuration = config.get_section(config.config_ini_section)

# URL приоритетно берём из переменной окружения `ALEMBIC_SQLALCHEMY_URL`,
# иначе — из `shared.config.DB_URL` (который читает `.env`).
#
# Это нужно для:
#   1) CI/тестов миграций, где удобно запускать `alembic upgrade head` на
#      временной SQLite, не трогая общий `.env`.
#   2) Production-деплоев, где хочется передать DSN через переменную окружения,
#      а не коммитить его в `.env`.
configuration["sqlalchemy.url"] = (
    os.environ.get("ALEMBIC_SQLALCHEMY_URL") or app_config.DB_URL
)

def run_migrations_offline() -> None:
    url = configuration["sqlalchemy.url"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())