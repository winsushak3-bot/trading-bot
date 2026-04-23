from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.core import session_maker


async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency для получения сессии БД в FastAPI.
    Автоматически коммитит при успехе, откатывает при ошибке.
    """
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
