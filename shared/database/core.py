# database/core.py

# IMPORTS

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from shared.config import config

# DATABASE ENGINE
#
# Параметры пула актуальны только для серверных БД (PostgreSQL/MySQL).
# Для SQLite SQLAlchemy по умолчанию использует StaticPool, который НЕ
# принимает `pool_size`/`max_overflow` — передача этих аргументов приводит
# к TypeError на import-time. Поэтому формируем kwargs условно.

_engine_kwargs: dict = {"echo": False}
if not config.DB_URL.startswith("sqlite"):
    _engine_kwargs["pool_size"] = 20
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(url=config.DB_URL, **_engine_kwargs)

# SESSION FACTORY

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)