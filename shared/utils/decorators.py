# utils/decorators.py
from functools import wraps
from typing import Callable


def admin_required(handler: Callable):
    """Декоратор для проверки прав администратора"""
    @wraps(handler)
    async def wrapper(message, *args, _: Callable, is_admin: bool, **kwargs):
        if is_admin is not True:
            await message.answer(_("no_admin_access"))
            return
        return await handler(message, *args, _=_, is_admin=is_admin, **kwargs)
    return wrapper
