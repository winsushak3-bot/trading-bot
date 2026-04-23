# handlers/profile/settings/settings.py

# IMPORTS

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.keyboards.profile import settings_kb
from bot.states import ProfileState
from bot.filters.localized_text import LocalizedText
from bot.handlers.common.back import back_registry
from bot.handlers.profile.profile import show_profile

router = Router()

# SETTINGS HANDLER

@router.message(LocalizedText("btn_settings"))
async def show_settings(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    """Отображает меню настроек профиля."""
    await state.set_state(ProfileState.settings)
    await message.answer(
        text=_("settings_title"),
        reply_markup=settings_kb(_)
    )

# BACK REGISTRY

back_registry.register(ProfileState.settings, show_profile)
