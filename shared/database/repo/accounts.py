# database/repo/accounts.py
import re
import logging
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError

from shared.database.models import BrokerAccount
from shared.services.cryptography import crypto
from shared.utils.exceptions import ValidationException, DatabaseException
from shared.constants import MIN_API_KEY_LENGTH, MIN_PASSWORD_LENGTH, MIN_EMAIL_LENGTH, EMAIL_PATTERN
from shared.database.repo.base import BaseRepo

logger = logging.getLogger(__name__)

class AccountRepo(BaseRepo):
    def _validate_account_data(self, api_key: str, password: str, account_name: str):
        """Валидация данных аккаунта перед сохранением"""
        # Проверка на пустоту
        if not api_key or not api_key.strip():
            raise ValidationException("API ключ не может быть пустым")
        if not password or not password.strip():
            raise ValidationException("Пароль не может быть пустым")
        if not account_name or not account_name.strip():
            raise ValidationException("Email не может быть пустым")
        
        # Проверка длины
        if len(api_key.strip()) < MIN_API_KEY_LENGTH:
            raise ValidationException(f"API ключ слишком короткий (минимум {MIN_API_KEY_LENGTH} символов)")
        if len(password.strip()) < MIN_PASSWORD_LENGTH:
            raise ValidationException(f"Пароль слишком короткий (минимум {MIN_PASSWORD_LENGTH} символов)")
        if len(account_name.strip()) < MIN_EMAIL_LENGTH:
            raise ValidationException(f"Email слишком короткий (минимум {MIN_EMAIL_LENGTH} символа)")
        
        # Проверка формата email
        if not re.match(EMAIL_PATTERN, account_name.strip()):
            raise ValidationException("Некорректный формат email")

    async def add_account(self, user_id: int, api_key: str, password: str, account_name: str, broker="capital"):
        """
        Добавляет новый аккаунт или обновляет существующий. 
        Автоматически шифрует данные перед записью.
        """
        self._validate_account_data(api_key, password, account_name)
        
        try:
            enc_key = crypto.encrypt(api_key.strip())
            enc_pass = crypto.encrypt(password.strip())

            # Ищем существующий аккаунт
            stmt = select(BrokerAccount).where(
                (BrokerAccount.user_id == user_id) & 
                (BrokerAccount.broker_name == broker)
            )
            result = await self.session.execute(stmt)
            account = result.scalar_one_or_none()

            if account:
                # Обновляем существующий
                account.account_name = account_name.strip()
                account.api_key_enc = enc_key
                account.password_enc = enc_pass
                account.is_demo = True
                account.is_active = True
            else:
                # Создаем новый
                account = BrokerAccount(
                    user_id=user_id,
                    broker_name=broker,
                    account_name=account_name.strip(),
                    api_key_enc=enc_key,
                    password_enc=enc_pass,
                    is_demo=True,
                    is_active=True
                )
                self.session.add(account)
                
            await self.session.flush()
            # Санитизация для логов: убираем переносы строк
            safe_account_name = account_name.replace('\n', '').replace('\r', '')
            logger.info(f"[ACCOUNT_UPSERT] user_id={user_id}, broker={broker}, account={safe_account_name}")
            return account
        except OperationalError as e:
            logger.error(f"OperationalError при добавлении аккаунта для {user_id}: {e}")
            raise DatabaseException("Ошибка соединения с базой данных")
        except DatabaseError as e:
            logger.error(f"DatabaseError при добавлении аккаунта для {user_id}: {e}")
            raise DatabaseException("Ошибка базы данных")

    async def get_account(self, user_id: int, broker="capital") -> dict | None:
        """
        Получает аккаунт и РАСШИФРОВЫВАЕТ данные.
        Возвращает чистый dict: {'api_key': '...', 'password': '...'}
        """
        stmt = select(BrokerAccount).where(
            (BrokerAccount.user_id == user_id) & 
            (BrokerAccount.broker_name == broker) &
            (BrokerAccount.is_active.is_(True))
        )
        result = await self.session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            return None

        # Расшифровываем
        try:
            return {
                "id": account.id,
                "account_name": account.account_name,
                "api_key": crypto.decrypt(account.api_key_enc),
                "password": crypto.decrypt(account.password_enc),
                "is_demo": account.is_demo
            }
        except Exception as e:
            # Если ключ шифрования сменился и мы не можем расшифровать
            logger.error(f"Failed to decrypt account data for user_id={user_id}: {e}")
            return None

    async def delete_account(self, user_id: int, broker="capital"):
        """Удаляет аккаунт."""
        stmt = delete(BrokerAccount).where(
            (BrokerAccount.user_id == user_id) & 
            (BrokerAccount.broker_name == broker)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        if result.rowcount > 0:
            logger.info(f"[ACCOUNT_DELETE] user_id={user_id}, broker={broker}")