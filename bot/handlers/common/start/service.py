# handlers/common/start/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.repo.users import UserRepo
from shared.database.models import User
from shared.utils.validator import UserDataValidator
from shared.utils.exceptions import ValidationException


async def get_or_create_user(
    session: AsyncSession, 
    tg_id: int, 
    username: str, 
    start_args: str | None
) -> tuple[User, bool]:
    """
    Получает пользователя или создает нового.
    
    Args:
        session: Сессия БД
        tg_id: ID пользователя Telegram
        username: Username пользователя Telegram
        start_args: Аргументы из команды /start (для рефералки)
        
    Returns:
        Кортеж (User, is_new) - пользователь и флаг создания
        
    Raises:
        ValidationException: Если данные некорректны
    """
    # Валидируем входные данные
    is_valid, msg = UserDataValidator.validate_username(username)
    if not is_valid:
        raise ValidationException(msg)
    
    # Проверяем tg_id
    if not isinstance(tg_id, int) or tg_id <= 0:
        raise ValidationException("Некорректный ID пользователя Telegram")
    
    repo = UserRepo(session)
    
    # 1. Пробуем найти пользователя
    user = await repo.get_user(tg_id)
    if user:
        return user, False

    # 2. Обработка рефералки
    referrer_id = None
    if start_args and start_args.strip().isdigit():
        # Очищаем от пробелов перед преобразованием
        try:
            possible_referrer_id = int(start_args.strip())
            if possible_referrer_id != tg_id and possible_referrer_id > 0:
                referrer = await repo.get_user(possible_referrer_id)
                if referrer:
                    referrer_id = possible_referrer_id
        except ValueError:
            pass  # Игнорируем некорректные значения рефералки

    # 3. Создаем нового пользователя
    new_user = await repo.create_user(
        tg_id=tg_id,
        username=username,
        referrer_id=referrer_id
    )
    
    return new_user, True