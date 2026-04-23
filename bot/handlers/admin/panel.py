# handlers/admin/panel.py

# IMPORTS

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from typing import Callable

from bot.filters.localized_text import LocalizedText
from bot.handlers.admin.keyboards.main import admin_main_kb
from bot.handlers.common.back import back_registry
from bot.states import AdminState
from shared.utils.decorators import admin_required

router = Router()

# ADMIN PANEL ENTRY

@router.message(LocalizedText("btn_admin_panel"))
@admin_required
async def admin_panel_entry(
    message: types.Message,
    state: FSMContext,
    _: Callable,
    is_admin: bool,
):
    """Вход в админ-панель по кнопке Админ панель в главном меню"""
    await state.set_state(AdminState.main)
    await message.answer(
        text=_("admin_panel_title"),
        reply_markup=admin_main_kb(_),
    )

# BACK REGISTRY

back_registry.register(AdminState, admin_panel_entry)