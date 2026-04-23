# tests/integration/database/test_accounts_repo.py
"""
Интеграционные тесты для database/repo/accounts.py
Критично! Проверяем что API ключи сохраняются зашифрованными.
"""
import pytest

from shared.database.repo.accounts import AccountRepo
from shared.database.models.accounts import BrokerAccount
from shared.services.cryptography import crypto


@pytest.mark.asyncio
class TestAccountRepo:
    """Тесты репозитория брокерских аккаунтов."""
    
    async def test_add_account_success(self, db_session, test_account_data):
        """Тест: Успешное добавление аккаунта."""
        repo = AccountRepo(db_session)
        
        account = await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key=test_account_data["api_key"],
            password=test_account_data["password"],
            account_name=test_account_data["account_name"]
        )
        
        assert account is not None
        assert account.user_id == test_account_data["user_id"]
        assert account.account_name == test_account_data["account_name"]
    
    async def test_add_account_encrypts_data(self, db_session, test_account_data):
        """Тест: Данные шифруются перед сохранением в БД."""
        repo = AccountRepo(db_session)
        
        await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key=test_account_data["api_key"],
            password=test_account_data["password"],
            account_name=test_account_data["account_name"]
        )
        
        # Читаем напрямую из БД
        from sqlalchemy import select
        stmt = select(BrokerAccount).where(BrokerAccount.user_id == test_account_data["user_id"])
        result = await db_session.execute(stmt)
        account = result.scalar_one()
        
        # Проверяем что данные зашифрованы (не равны оригиналу)
        assert account.api_key_enc != test_account_data["api_key"]
        assert account.password_enc != test_account_data["password"]
        
        # Проверяем что можем расшифровать
        decrypted_key = crypto.decrypt(account.api_key_enc)
        decrypted_pass = crypto.decrypt(account.password_enc)
        
        assert decrypted_key == test_account_data["api_key"]
        assert decrypted_pass == test_account_data["password"]
    
    async def test_get_account_decrypts_data(self, db_session, test_account_data):
        """Тест: get_account расшифровывает данные."""
        repo = AccountRepo(db_session)
        
        # Добавляем аккаунт
        await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key=test_account_data["api_key"],
            password=test_account_data["password"],
            account_name=test_account_data["account_name"]
        )
        
        # Получаем аккаунт
        account = await repo.get_account(user_id=test_account_data["user_id"])
        
        assert account is not None
        assert account["api_key"] == test_account_data["api_key"]
        assert account["password"] == test_account_data["password"]
        assert account["account_name"] == test_account_data["account_name"]
    
    async def test_get_nonexistent_account(self, db_session):
        """Тест: Получение несуществующего аккаунта возвращает None."""
        repo = AccountRepo(db_session)
        
        account = await repo.get_account(user_id=999999999)
        
        assert account is None
    
    async def test_delete_account(self, db_session, test_account_data):
        """Тест: Удаление аккаунта."""
        repo = AccountRepo(db_session)
        
        # Добавляем аккаунт
        await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key=test_account_data["api_key"],
            password=test_account_data["password"],
            account_name=test_account_data["account_name"]
        )
        
        # Проверяем что аккаунт существует
        account = await repo.get_account(user_id=test_account_data["user_id"])
        assert account is not None
        
        # Удаляем
        await repo.delete_account(user_id=test_account_data["user_id"])
        
        # Проверяем что аккаунт удален
        account = await repo.get_account(user_id=test_account_data["user_id"])
        assert account is None
    
    async def test_add_account_replaces_old(self, db_session, test_account_data):
        """Тест: Добавление нового аккаунта удаляет старый."""
        repo = AccountRepo(db_session)
        
        # Добавляем первый аккаунт
        await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key="old_api_key",
            password="old_password",
            account_name="old@example.com"
        )
        
        # Добавляем второй аккаунт (должен заменить первый)
        await repo.add_account(
            user_id=test_account_data["user_id"],
            api_key=test_account_data["api_key"],
            password=test_account_data["password"],
            account_name=test_account_data["account_name"]
        )
        
        # Проверяем что остался только новый аккаунт
        account = await repo.get_account(user_id=test_account_data["user_id"])
        
        assert account["api_key"] == test_account_data["api_key"]
        assert account["password"] == test_account_data["password"]
        assert account["account_name"] == test_account_data["account_name"]
    
    async def test_add_account_with_special_characters(self, db_session):
        """Тест: Сохранение аккаунта со спецсимволами в данных."""
        repo = AccountRepo(db_session)
        
        special_data = {
            "user_id": 123456789,
            "api_key": "key!@#$%^&*()",
            "password": "pass<>?:\"{}|",
            "account_name": "test+special@example.com"
        }
        
        await repo.add_account(**special_data)
        
        account = await repo.get_account(user_id=special_data["user_id"])
        
        assert account["api_key"] == special_data["api_key"]
        assert account["password"] == special_data["password"]
    
    async def test_multiple_users_different_accounts(self, db_session):
        """Тест: Разные пользователи могут иметь свои аккаунты."""
        repo = AccountRepo(db_session)
        
        # Добавляем аккаунт для пользователя 1
        await repo.add_account(
            user_id=111,
            api_key="key_user_1",
            password="pass_user_1",
            account_name="user1@example.com"
        )
        
        # Добавляем аккаунт для пользователя 2
        await repo.add_account(
            user_id=222,
            api_key="key_user_2",
            password="pass_user_2",
            account_name="user2@example.com"
        )
        
        # Проверяем что оба аккаунта существуют и не перепутаны
        account1 = await repo.get_account(user_id=111)
        account2 = await repo.get_account(user_id=222)
        
        assert account1["api_key"] == "key_user_1"
        assert account2["api_key"] == "key_user_2"


@pytest.mark.asyncio
class TestAccountRepoEdgeCases:
    """Тесты граничных случаев."""
    
    async def test_add_account_empty_strings(self, db_session):
        """Тест: Добавление аккаунта с пустыми строками должно выбрасывать ValidationException."""
        from shared.utils.exceptions import ValidationException
        repo = AccountRepo(db_session)
        
        with pytest.raises(ValidationException):
            await repo.add_account(
                user_id=123,
                api_key="",
                password="",
                account_name=""
            )
    
    async def test_delete_nonexistent_account(self, db_session):
        """Тест: Удаление несуществующего аккаунта не падает."""
        repo = AccountRepo(db_session)
        
        # Не должно быть ошибки
        await repo.delete_account(user_id=999999999)
