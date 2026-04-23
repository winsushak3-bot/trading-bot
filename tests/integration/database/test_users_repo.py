# tests/integration/database/test_users_repo.py
"""
Интеграционные тесты для database/repo/users.py
Проверяем работу с пользователями в БД.
"""
import pytest
from datetime import datetime

from shared.database.repo.users import UserRepo


@pytest.mark.asyncio
class TestUserRepo:
    """Тесты репозитория пользователей."""
    
    async def test_create_user(self, db_session):
        """Тест: Создание пользователя."""
        repo = UserRepo(db_session)
        
        user = await repo.create_user(tg_id=123456, username="testuser", language="ru")
        
        assert user.tg_id == 123456
        assert user.username == "testuser"
        assert user.language == "ru"
    
    async def test_create_user_with_referrer(self, db_session):
        """Тест: Создание пользователя с реферером."""
        repo = UserRepo(db_session)
        
        # Создаем реферера
        referrer = await repo.create_user(tg_id=111, username="referrer")
        
        # Создаем реферала
        user = await repo.create_user(tg_id=222, username="referral", referrer_id=111)
        
        assert user.referrer_id == 111
        
        # Проверяем что счетчик реферера увеличился
        updated_referrer = await repo.get_user(111)
        assert updated_referrer.referrals_count == 1
    
    async def test_get_user_exists(self, db_session):
        """Тест: Получение существующего пользователя."""
        repo = UserRepo(db_session)
        
        await repo.create_user(tg_id=123, username="test")
        
        user = await repo.get_user(123)
        
        assert user is not None
        assert user.tg_id == 123
    
    async def test_get_user_not_exists(self, db_session):
        """Тест: Получение несуществующего пользователя."""
        repo = UserRepo(db_session)
        
        user = await repo.get_user(999999)
        
        assert user is None
    
    async def test_update_language(self, db_session):
        """Тест: Обновление языка."""
        repo = UserRepo(db_session)
        
        await repo.create_user(tg_id=123, language="ru")
        
        await repo.update_language(123, "en")
        
        user = await repo.get_user(123)
        assert user.language == "en"
    
    async def test_update_nickname(self, db_session):
        """Тест: Обновление никнейма."""
        repo = UserRepo(db_session)
        
        await repo.create_user(tg_id=123)
        
        await repo.update_nickname(123, "Shadow")
        
        user = await repo.get_user(123)
        assert user.nickname == "Shadow"
        assert user.nickname_updated_at is not None
    
    async def test_toggle_notifications(self, db_session):
        """Тест: Переключение уведомлений."""
        repo = UserRepo(db_session)
        
        await repo.create_user(tg_id=123)
        
        await repo.toggle_notifications(123, False)
        
        user = await repo.get_user(123)
        assert user.notifications_enabled is False
        
        await repo.toggle_notifications(123, True)
        
        user = await repo.get_user(123)
        assert user.notifications_enabled is True
    
@pytest.mark.asyncio
class TestUserRepoEdgeCases:
    """Тесты граничных случаев."""
    
    async def test_create_user_without_username(self, db_session):
        """Тест: Создание пользователя без username."""
        repo = UserRepo(db_session)
        
        user = await repo.create_user(tg_id=123)
        
        assert user.username is None
    
    async def test_multiple_referrals(self, db_session):
        """Тест: Несколько рефералов у одного реферера."""
        repo = UserRepo(db_session)
        
        await repo.create_user(tg_id=111, username="referrer")
        
        await repo.create_user(tg_id=222, referrer_id=111)
        await repo.create_user(tg_id=333, referrer_id=111)
        await repo.create_user(tg_id=444, referrer_id=111)
        
        referrer = await repo.get_user(111)
        assert referrer.referrals_count == 3
