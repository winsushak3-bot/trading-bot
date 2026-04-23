# handlers/common/__init__.py
from aiogram import Router

from .start import router as start_router
from .onboarding import router as onboarding_router
from .back import router as back_router
from . import chat_commands

router = Router()
router.include_router(start_router)
router.include_router(onboarding_router)
router.include_router(chat_commands.router)
router.include_router(back_router)

__all__ = ["router"]
