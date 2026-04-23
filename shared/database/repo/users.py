# database/repo/users.py
import logging
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from shared.database.models import User
from shared.utils.exceptions import DatabaseException
from shared.database.repo.base import BaseRepo

logger = logging.getLogger(__name__)

class UserRepo(BaseRepo):
    async def _update_user(self, tg_id: int, **values):
        """Базовый метод для обновления пользователя"""
        try:
            stmt = update(User).where(User.tg_id == tg_id).values(**values)
            await self.session.execute(stmt)
        except OperationalError as e:
            logger.error(f"OperationalError при обновлении пользователя {tg_id}: {e}")
            raise DatabaseException("Ошибка соединения с базой данных")
        except DatabaseError as e:
            logger.error(f"DatabaseError при обновлении пользователя {tg_id}: {e}")
            raise DatabaseException("Ошибка базы данных")

    async def get_user(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, tg_id: int, username: str = None, language: str = "ru", referrer_id: int = None) -> User:
        try:
            user = User(
                tg_id=tg_id, 
                username=username, 
                language=language,
                referrer_id=referrer_id,
                nickname_updated_at=func.now()
            )
            self.session.add(user)
            if referrer_id:
                stmt = update(User).where(User.tg_id == referrer_id).values(
                    referrals_count=User.referrals_count + 1
                )
                await self.session.execute(stmt)
            # Commit выполняется вызывающим кодом (middleware или ручной)
            logger.info(f"[USER_CREATE] tg_id={tg_id}, username={username}, referrer={referrer_id}")
            return user
        except IntegrityError as e:
            logger.error(f"IntegrityError при создании пользователя {tg_id}: {e}")
            raise DatabaseException("Пользователь с таким ID уже существует")
        except OperationalError as e:
            logger.error(f"OperationalError при создании пользователя {tg_id}: {e}")
            raise DatabaseException("Ошибка соединения с базой данных")
        except DatabaseError as e:
            logger.error(f"DatabaseError при создании пользователя {tg_id}: {e}")
            raise DatabaseException("Ошибка базы данных")

    async def update_language(self, tg_id: int, language: str):
        await self._update_user(tg_id, language=language)

    async def update_nickname(self, tg_id: int, new_nickname: str):
        stmt = update(User).where(User.tg_id == tg_id).values(
            nickname=new_nickname,
            nickname_updated_at=func.now()
        )
        await self.session.execute(stmt)

    async def toggle_notifications(self, tg_id: int, enabled: bool):
        await self._update_user(tg_id, notifications_enabled=enabled)

    async def is_nickname_taken(self, nickname: str) -> bool:
        """Проверяет, занят ли никнейм."""
        stmt = select(User).where(User.nickname == nickname)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_stats(self) -> dict:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)

        total = (await self.session.execute(select(func.count()).select_from(User))).scalar_one()
        new_today = (await self.session.execute(
            select(func.count()).select_from(User).where(User.created_at >= today_start)
        )).scalar_one()
        new_week = (await self.session.execute(
            select(func.count()).select_from(User).where(User.created_at >= week_start)
        )).scalar_one()
        with_notif = (await self.session.execute(
            select(func.count()).select_from(User).where(User.notifications_enabled == True)
        )).scalar_one()
        with_nickname = (await self.session.execute(
            select(func.count()).select_from(User).where(User.nickname.isnot(None))
        )).scalar_one()

        return {
            "total": total,
            "new_today": new_today,
            "new_week": new_week,
            "with_notifications": with_notif,
            "with_nickname": with_nickname,
        }

    @staticmethod
    def _escape_like(value: str) -> str:
        """Экранирование спецсимволов LIKE: %, _, \\"""
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    async def get_all_users(self, limit: int = 20, offset: int = 0, search: str = "") -> list[User]:
        stmt = select(User).order_by(User.created_at.desc())
        if search:
            safe = self._escape_like(search)
            stmt = stmt.where(
                or_(
                    User.username.ilike(f"%{safe}%"),
                    User.nickname.ilike(f"%{safe}%"),
                )
            )
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_users(self, search: str = "") -> int:
        stmt = select(func.count()).select_from(User)
        if search:
            safe = self._escape_like(search)
            stmt = stmt.where(
                or_(
                    User.username.ilike(f"%{safe}%"),
                    User.nickname.ilike(f"%{safe}%"),
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar_one()