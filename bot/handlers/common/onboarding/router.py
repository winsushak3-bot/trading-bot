# handlers/common/onboarding/router.py
import re
from typing import Callable
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder 
from sqlalchemy.ext.asyncio import AsyncSession

from shared.utils.i18n import i18n
from shared.utils.cache import set_user_lang
from bot.states import OnboardingState
from bot.handlers.keyboards.main_menu import main_menu_kb
from .service import update_language, set_nickname
from shared.constants import NICKNAME_PATTERN

router = Router()
NICK_REGEX = re.compile(NICKNAME_PATTERN)

# 1. ОБРАБОТКА ВЫБОРА ЯЗЫКА
@router.callback_query(OnboardingState.language, F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    
    # Сохраняем в БД
    await update_language(session, callback.from_user.id, lang_code)
    
    # ОБНОВЛЯЕМ КЕШ REDIS через утилиту
    storage = state.storage
    redis = getattr(storage, "redis", None)
    if redis:
        await set_user_lang(redis, callback.from_user.id, lang_code)
    
    # Хак для смены языка на лету
    def new_i18n(key, **kwargs):
        return i18n.get(key, lang=lang_code, **kwargs)

    lang_name = new_i18n(f"lang_{lang_code}")
    await callback.answer(new_i18n("lang_selected", named_lang=lang_name))
    
    # Переходим к вводу ника
    await state.set_state(OnboardingState.nickname_input)
    await callback.message.delete()
    # Правильный ключ
    await callback.message.answer(new_i18n("ask_nickname"))


# 2. ВВОД НИКА
@router.message(OnboardingState.nickname_input)
async def process_nickname(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    nickname = message.text.strip()

    # Валидация
    if not NICK_REGEX.match(nickname):
        await message.answer(_("nick_invalid_format"))
        return

    # Сохраняем для подтверждения
    await state.update_data(pending_nickname=nickname)
    await state.set_state(OnboardingState.nickname_confirm)

    builder = InlineKeyboardBuilder()
    builder.button(text=_("nick_btn_confirm"), callback_data="nick_ok")
    builder.button(text=_("nick_btn_retry"), callback_data="nick_retry")
    builder.adjust(1)

    await message.answer(
        text=_("nick_confirm_ask", nickname=nickname),
        reply_markup=builder.as_markup()
    )

# 3. ЕСЛИ НАЖАЛИ "ИЗМЕНИТЬ"
@router.callback_query(OnboardingState.nickname_confirm, F.data == "nick_retry")
async def retry_nickname(callback: types.CallbackQuery, _: Callable, state: FSMContext):
    await state.set_state(OnboardingState.nickname_input)
    await callback.message.edit_text(_("ask_nickname"))

# 4. ЕСЛИ НАЖАЛИ "ПОДТВЕРДИТЬ"
@router.callback_query(OnboardingState.nickname_confirm, F.data == "nick_ok")
async def confirm_nickname(callback: types.CallbackQuery, session: AsyncSession, _: Callable, state: FSMContext):
    data = await state.get_data()
    nickname = data.get("pending_nickname")

    # Проверяем уникальность ника ДО записи — избегаем IntegrityError + rollback,
    # который ломает состояние сессии для DbSessionMiddleware.
    from shared.database.repo.users import UserRepo
    repo = UserRepo(session)
    if await repo.is_nickname_taken(nickname):
        await callback.message.edit_text(_("nick_taken", nickname=nickname))
        await state.set_state(OnboardingState.nickname_input)
        await callback.message.answer(_("ask_nickname"))
        return

    await set_nickname(session, callback.from_user.id, nickname)
    await session.flush()
    
    await callback.message.delete()
    await state.clear()
    
    await callback.message.answer(
        text=_("nick_success", nickname=nickname),
        reply_markup=main_menu_kb(_, callback.from_user.id)
    )