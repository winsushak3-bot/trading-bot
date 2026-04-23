# handlers/common/start/router.py
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем нашу новую функцию навигации
from bot.handlers.common.navigation import nav_start

router = Router()

@router.message(CommandStart())
async def cmd_start(
    message: types.Message, 
    session: AsyncSession, 
    _: Callable,
    is_admin: bool,
    state: FSMContext, 
    command: CommandObject = None 
):
    """
    Точка входа /start. 
    Теперь просто передает управление в навигатор.
    """
    args = command.args if command else None
    await nav_start(message, session, _, state, start_args=args, is_admin=is_admin)