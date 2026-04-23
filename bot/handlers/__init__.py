# handlers/__init__.py
from aiogram import Router

from .common import router as common_router
from .profile import router as profile_router
from .admin import router as admin_router

root_router = Router()
root_router.include_router(common_router)
root_router.include_router(profile_router)
root_router.include_router(admin_router)

__all__ = ["root_router"]
