from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.schemas import TelegramAuthRequest, AuthResponse
from backend.core.security import validate_telegram_init_data
from backend.core.deps import get_session
from shared.database.repo.users import UserRepo
from shared.utils.exceptions import DatabaseException

router = APIRouter()


@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(
    request: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Авторизация через Telegram WebApp initData.
    """
    # Валидируем initData
    user_data = validate_telegram_init_data(request.init_data)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")
    
    user_id = user_data.get('id')
    username = user_data.get('username')
    first_name = user_data.get('first_name')
    
    # Проверяем/создаем пользователя в БД
    user_repo = UserRepo(session)
    db_user = await user_repo.get_user(user_id)
    
    if not db_user:
        try:
            db_user = await user_repo.create_user(
                tg_id=user_id,
                username=username,
                language="ru"
            )
        except DatabaseException:
            # Пользователь уже существует (race condition) — просто получаем
            await session.rollback()
            db_user = await user_repo.get_user(user_id)
    
    return AuthResponse(
        success=True,
        user_id=user_id,
        username=username,
        first_name=first_name
    )
