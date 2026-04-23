# handlers/profile/settings/language/language.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.keyboards.profile import language_inline_kb, language_confirm_kb, settings_kb
from shared.utils.i18n import i18n
from shared.utils.cache import set_user_lang
from bot.states import ProfileState
from shared.database.repo.users import UserRepo
from bot.filters.localized_text import LocalizedText

from bot.handlers.common.back import back_registry
from bot.handlers.profile.settings.settings import show_settings

router = Router()

def get_lang_name(lang_code: str, translate_func: Callable) -> str:
    names = {
        "ru": translate_func("lang_ru"),
        "ua": translate_func("lang_ua"),
        "en": translate_func("lang_en")
    }
    return names.get(lang_code, lang_code)

@router.message(LocalizedText("btn_language"))
async def show_language(message: types.Message, session: AsyncSession, _: Callable, state: FSMContext):
    await state.set_state(ProfileState.language)

    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)
    current_lang = user.language if user else "ru"

    await message.answer(
        text=_("language_title", named_lang=get_lang_name(current_lang, _)),
        reply_markup=language_inline_kb(_)
    )

@router.callback_query(ProfileState.language, F.data.startswith("lang_"))
async def ask_confirm(callback: types.CallbackQuery, _: Callable):
    target_lang_code = callback.data.split("_")[1]
    target_lang_name = get_lang_name(target_lang_code, _)

    text = _("ask_confirm_change", target_lang=target_lang_name)

    await callback.message.edit_text(
        text=text,
        reply_markup=language_confirm_kb(_, target_lang_code)
    )
    await callback.answer()

@router.callback_query(ProfileState.language, F.data == "cancel_lang_change")
async def cancel_change(callback: types.CallbackQuery, session: AsyncSession, _: Callable):
    repo = UserRepo(session)
    user = await repo.get_user(callback.from_user.id)
    current_lang = user.language if user else "ru"

    await callback.message.edit_text(
        text=_("language_title", named_lang=get_lang_name(current_lang, _)),
        reply_markup=language_inline_kb(_)
    )
    await callback.answer(_("btn_back"))

@router.callback_query(ProfileState.language, F.data.startswith("conf_lang_"))
async def confirm_change(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    target_lang_code = callback.data.split("_")[2]

    repo = UserRepo(session)
    await repo.update_language(callback.from_user.id, target_lang_code)

    # Инвалидируем кеш и сохраняем новый язык С TTL
    storage = state.storage
    redis = getattr(storage, "redis", None)
    if redis:
        await set_user_lang(redis, callback.from_user.id, target_lang_code)

    def new_i18n(key, **kwargs):
        return i18n.get(key, lang=target_lang_code, **kwargs)

    target_lang_name = get_lang_name(target_lang_code, new_i18n)

    await callback.answer(new_i18n("lang_selected", named_lang=target_lang_name))
    await callback.message.delete()
    await state.set_state(ProfileState.settings)

    await callback.message.answer(
        text=new_i18n("lang_changed_success", named_lang=target_lang_name),
        reply_markup=settings_kb(new_i18n)
    )

back_registry.register(ProfileState.language, show_settings)
