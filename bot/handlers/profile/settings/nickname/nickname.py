# handlers/profile/settings/nickname/nickname.py
import logging
import re
from datetime import datetime, timezone
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.repo.users import UserRepo
from shared.constants import NICKNAME_CHANGE_COOLDOWN_DAYS, NICKNAME_PATTERN
from bot.states import ProfileState
from bot.handlers.keyboards.profile import confirm_nick_kb, settings_kb, change_nick_start_kb
from bot.filters.localized_text import LocalizedText

from bot.handlers.common.back import back_registry
from bot.handlers.profile.settings.settings import show_settings

logger = logging.getLogger(__name__)

router = Router()
NICK_REGEX = re.compile(NICKNAME_PATTERN)

@router.message(LocalizedText("btn_change_nick"))
async def show_nick_info(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    """Показывает информацию о текущем нике и дате последнего изменения."""
    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)

    if user.nickname_updated_at:
        date_str = user.nickname_updated_at.strftime('%d.%m.%Y')
    else:
        date_str = user.created_at.strftime('%d.%m.%Y')

    await message.answer(
        text=_("nick_info_title", nickname=user.nickname, date=date_str),
        reply_markup=change_nick_start_kb(_)
    )

@router.callback_query(F.data == "start_change_nick", ProfileState.settings)
async def start_change_nick(callback: types.CallbackQuery, session: AsyncSession, _: Callable, state: FSMContext):
    """Проверяет cooldown и запускает процесс смены ника."""
    repo = UserRepo(session)
    user = await repo.get_user(callback.from_user.id)

    if user.nickname_updated_at:
        last_update = user.nickname_updated_at
        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        delta = now - last_update
        
        if delta.days < NICKNAME_CHANGE_COOLDOWN_DAYS:
            days_left = NICKNAME_CHANGE_COOLDOWN_DAYS - delta.days
            logger.warning(f"[COOLDOWN_BLOCK] tg_id={callback.from_user.id}, action=nick_change, days_left={days_left}")
            await callback.answer(_("nick_cooldown_error", days=days_left), show_alert=True)
            return

    await state.set_state(ProfileState.nick_change_input)
    await callback.message.edit_text(_("nick_change_ask"))

@router.message(ProfileState.nick_change_input)
async def process_new_nick(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    """Обрабатывает ввод нового ника и проверяет его уникальность."""
    nickname = message.text.strip()
    if not NICK_REGEX.match(nickname):
        await message.answer(_("nick_invalid_format"))
        return

    repo = UserRepo(session)
    is_taken = await repo.is_nickname_taken(nickname)

    if is_taken:
        await message.answer(_("nick_taken", nickname=nickname))
        return

    await state.update_data(new_nick=nickname)
    await state.set_state(ProfileState.nick_change_confirm)

    await message.answer(
        text=_("nick_change_confirm", nickname=nickname),
        reply_markup=confirm_nick_kb(_)
    )

@router.callback_query(F.data == "confirm_new_nick", ProfileState.nick_change_confirm)
async def confirm_change(callback: types.CallbackQuery, session: AsyncSession, _: Callable, state: FSMContext):
    """Подтверждает смену ника и сохраняет в БД."""
    data = await state.get_data()
    new_nick = data.get("new_nick")
    repo = UserRepo(session)
    user = await repo.get_user(callback.from_user.id)
    old_nick = user.nickname if user else "Unknown"
    
    await repo.update_nickname(callback.from_user.id, new_nick)
    logger.info(f"[NICK_CHANGE] tg_id={callback.from_user.id}, old_nick={old_nick}, new_nick={new_nick}")
    
    await callback.message.delete()
    await state.set_state(ProfileState.settings)
    await callback.message.answer(text=_("nick_change_success", nickname=new_nick), reply_markup=settings_kb(_))

@router.callback_query(F.data == "cancel_change_nick", ProfileState.nick_change_confirm)
async def cancel_change(callback: types.CallbackQuery, _: Callable, state: FSMContext):
    """Отменяет смену ника и возвращает в настройки."""
    await callback.message.delete()
    await state.set_state(ProfileState.settings)
    await callback.message.answer(_("settings_title"), reply_markup=settings_kb(_))

back_registry.register(ProfileState.nick_change_input, show_settings)
back_registry.register(ProfileState.nick_change_confirm, show_settings)
