# handlers/profile/profile.py

# IMPORTS

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.repo.users import UserRepo
from bot.handlers.keyboards.profile import profile_kb
from bot.states import ProfileState
from bot.filters.localized_text import LocalizedText
from bot.handlers.common.back import back_registry
from bot.handlers.common.navigation import nav_start

router = Router()

# PROFILE HANDLER

@router.message(LocalizedText("btn_profile"))
async def show_profile(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    """Отображает профиль пользователя с ID, ником и датой регистрации."""
    await state.set_state(ProfileState.main)

    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)

    if not user:
        nickname = "Unknown"
        username = "Unknown"
        reg_date = "N/A"
    else:
        nickname = user.nickname or _('no_username')
        username = f"@{user.username}" if user.username else _('no_username')
        reg_date = user.created_at.strftime('%Y-%m-%d')

    text = (
        f"{_('profile_title')}\n\n"
        f"╔ <b>{_('label_id')}</b> <code>{message.from_user.id}</code>\n"
        f"╠ <b>{_('label_nik')}</b> <code>#{nickname}</code>\n"
        f"╠ <b>{_('label_username')}</b> <code>{username}</code>\n"
        f"╚ <b>{_('label_reg')}</b> <code>{reg_date}</code>"
    )

    await message.answer(text=text, reply_markup=profile_kb(_))

# BACK REGISTRY

back_registry.register(ProfileState.main, nav_start)
