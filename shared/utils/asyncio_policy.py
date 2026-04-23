"""
Единая настройка asyncio event-loop policy.

На Windows Python 3.8+ по умолчанию использует `ProactorEventLoop`, что ломает
asyncpg / aiodns (WinError 64, ConnectionResetError). Нужно явно включить
`WindowsSelectorEventLoopPolicy` в каждом entry-point, который запускается
без uvicorn (uvicorn делает это сам).
"""

from __future__ import annotations

import asyncio
import sys


def apply_windows_event_loop_policy() -> None:
    """Установить selector-based loop на Windows. No-op на других ОС."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
