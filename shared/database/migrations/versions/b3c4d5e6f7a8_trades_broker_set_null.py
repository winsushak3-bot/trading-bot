"""trades.broker_account_id: CASCADE -> SET NULL

Revision ID: b3c4d5e6f7a8
Revises: a2f8b1c4d9e0
Create Date: 2026-04-17 15:10:00.000000

Меняет ON DELETE для FK `trades.broker_account_id → broker_accounts.id`
с CASCADE на SET NULL.

Зачем: ранее удаление брокерского аккаунта (например, при «Отключить
брокера») каскадно стирало ВСЮ историю сделок пользователя. Для
финансового приложения это недопустимо — история должна оставаться для
аналитики / PnL-графиков / налоговой отчётности. Теперь при удалении
аккаунта сделки просто отвязываются от него (`broker_account_id = NULL`).

Используем `batch_alter_table`, чтобы миграция работала и на PostgreSQL
(делает drop_constraint + create_constraint), и на SQLite
(пересоздаёт таблицу через временную копию — SQLite не умеет ALTER FK).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a2f8b1c4d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Имя FK-ограничения создаётся Alembic'ом автоматически (anonymous) —
# `trades_broker_account_id_fkey` на PostgreSQL. Указываем явно:
_FK_NAME = "trades_broker_account_id_fkey"


def upgrade() -> None:
    with op.batch_alter_table("trades") as batch_op:
        # Сначала убираем старый CASCADE-FK.
        batch_op.drop_constraint(_FK_NAME, type_="foreignkey")
        # Создаём новый FK с SET NULL.
        batch_op.create_foreign_key(
            _FK_NAME,
            "broker_accounts",
            ["broker_account_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("trades") as batch_op:
        batch_op.drop_constraint(_FK_NAME, type_="foreignkey")
        batch_op.create_foreign_key(
            _FK_NAME,
            "broker_accounts",
            ["broker_account_id"],
            ["id"],
            ondelete="CASCADE",
        )
