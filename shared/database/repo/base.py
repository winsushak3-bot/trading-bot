# database/repo/base.py
"""Base repository class — eliminates repetitive __init__(self, session) boilerplate."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    """Base class for all repository classes."""

    def __init__(self, session: AsyncSession):
        self.session = session
