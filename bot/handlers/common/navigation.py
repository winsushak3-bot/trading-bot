# handlers/common/navigation.py
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states import OnboardingState
from bot.handlers.keyboards.main_menu import main_menu_kb
from bot.handlers.keyboards.profile import language_inline_kb
from bot.handlers.common.start.service import get_or_create_user
from shared.utils.i18n import i18n

logger = logging.getLogger(__name__)

async def nav_start(
    message: types.Message,
    session: AsyncSession,
    _: Callable,
    state: FSMContext,
    start_args: str | None = None,
    is_admin: bool | None = None,
):
    """
    Универсальная функция перехода в главное меню.
    
    Используется командой /start и кнопкой 'Назад'.
    Для новых пользователей запускает onboarding.
    """
    # Сбрасываем старые состояния (например, если юзер был в середине процесса смены ника)
    current_state = await state.get_state()
    if current_state:
        await state.clear()

    # 1. Получаем или создаем юзера
    user, is_new = await get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        start_args=start_args
    )

    # 2. Логика новичка (или если нет ника)
    if is_new or user.nickname is None:
        # Уведомление рефереру (того, кто пригласил)
        if is_new and user.referrer_id:
            try:
                # Получаем реферера из БД для использования его языка
                from shared.database.repo.users import UserRepo
                repo = UserRepo(session)
                referrer = await repo.get_user(user.referrer_id)
                if referrer:
                    await message.bot.send_message(
                        chat_id=user.referrer_id,
                        text=i18n.get("new_referral_notification", lang=referrer.language)
                    )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление рефереру {user.referrer_id}: {e}")

        # Отправляем на выбор языка
        await state.set_state(OnboardingState.language)
        
        await message.answer(
            i18n.get("welcome_select_language", lang="ru"),
            reply_markup=language_inline_kb(_)
        )
    else:
        # 3. Логика старичка -> Главное меню
        await message.answer(
            text=_("start_back", nickname=user.nickname),
            reply_markup=main_menu_kb(_, message.from_user.id, is_admin=is_admin)
        )