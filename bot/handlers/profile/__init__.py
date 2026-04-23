# handlers/profile/__init__.py
from aiogram import Router

from . import profile as profile_main
from .settings import settings as profile_settings
from .settings.language import language as profile_language
from .settings.nickname import nickname as settings_nickname
from .settings.notifications import notifications as settings_notif

router = Router()
router.include_router(profile_language.router)
router.include_router(settings_nickname.router)
router.include_router(settings_notif.router)
router.include_router(profile_settings.router)
router.include_router(profile_main.router)

__all__ = ["router"]
