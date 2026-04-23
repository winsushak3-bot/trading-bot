# handlers/common/back/__init__.py
from .router import router
from .registry import back_registry

__all__ = ["router", "back_registry"]