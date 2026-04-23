# handlers/common/back/router.py
import inspect
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.localized_text import LocalizedText
from .registry import back_registry
from bot.handlers.common.navigation import nav_start
from shared.utils.logger import setup_logger

logger = setup_logger()

router = Router()


@router.message(LocalizedText("btn_back"))
async def universal_back(
    message: types.Message,
    session: AsyncSession,
    _: Callable,
    state: FSMContext,
    is_admin: bool | None = None,
):
    # 1. Узнаем текущее состояние
    current_state_str = await state.get_state()
    

    # 2. Ищем маршрут в реестре
    target_handler = back_registry.get_handler(current_state_str)

    # 2.1. Если мы в главном меню админки — выходим в главное меню пользователя
    if current_state_str == "AdminState:main":
        await nav_start(message, session, _, state, is_admin=is_admin)
        return

    # 3. Если маршрут не найден -> идем в Главное меню
    if not target_handler:
        await nav_start(message, session, _, state, is_admin=is_admin)
        return

    # 4. Если маршрут найден -> аккуратно вызываем функцию
    try:
        sig = inspect.signature(target_handler)
        params = sig.parameters
        
        # Собираем аргументы, которые ожидает функция
        kwargs = {}
        if 'message' in params:
            kwargs['message'] = message
        if 'session' in params:
            kwargs['session'] = session
        if '_' in params:
            kwargs['_'] = _
        if 'state' in params:
            kwargs['state'] = state
        if 'is_admin' in params:
            kwargs['is_admin'] = is_admin
            
        # Вызываем
        await target_handler(**kwargs)
            
    except Exception as e:
        logger.exception(f"❌ Critical Error in Back Navigation: {e}")
        # При любой ошибке спасаем юзера в главное меню
        await nav_start(message, session, _, state, is_admin=is_admin)