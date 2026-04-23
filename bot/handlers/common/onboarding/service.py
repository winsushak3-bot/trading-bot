# handlers/common/onboarding/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.repo.users import UserRepo

async def update_language(session: AsyncSession, user_id: int, lang_code: str):
    """Обновляет язык пользователя."""
    repo = UserRepo(session)
    await repo.update_language(user_id, lang_code)

async def set_nickname(session: AsyncSession, user_id: int, nickname: str):
    """Сохраняет никнейм пользователю."""
    repo = UserRepo(session)
    await repo.update_nickname(user_id, nickname)