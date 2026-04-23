# handlers/profile/settings/notifications/notifications.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.repo.users import UserRepo
from bot.states import ProfileState
from bot.filters.localized_text import LocalizedText
from bot.handlers.keyboards.profile import notifications_kb
from bot.handlers.keyboards.common import common_back_kb

from bot.handlers.common.back import back_registry
from bot.handlers.profile.settings.settings import show_settings

router = Router()

@router.message(LocalizedText("btn_notifications"))
async def show_notifications(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    await state.set_state(ProfileState.settings_notifications)

    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)

    if not user:
        return

    status_text = _("notif_on") if user.notifications_enabled else _("notif_off")

    await message.answer("👇", reply_markup=common_back_kb(_))

    await message.answer(
        _("notif_title", status=status_text),
        reply_markup=notifications_kb(_, user.notifications_enabled)
    )

@router.callback_query(F.data == "notif_disable", ProfileState.settings_notifications)
async def disable_notif(callback: types.CallbackQuery, session: AsyncSession, _: Callable):
    repo = UserRepo(session)
    await repo.toggle_notifications(callback.from_user.id, False)

    status_text = _("notif_off")
    await callback.message.edit_text(
        _("notif_title", status=status_text),
        reply_markup=notifications_kb(_, False)
    )
    await callback.answer(_("notif_off"))

@router.callback_query(F.data == "notif_enable", ProfileState.settings_notifications)
async def enable_notif(callback: types.CallbackQuery, session: AsyncSession, _: Callable):
    repo = UserRepo(session)
    await repo.toggle_notifications(callback.from_user.id, True)

    status_text = _("notif_on")
    await callback.message.edit_text(
        _("notif_title", status=status_text),
        reply_markup=notifications_kb(_, True)
    )
    await callback.answer(_("notif_on"))

back_registry.register(ProfileState.settings_notifications, show_settings)
