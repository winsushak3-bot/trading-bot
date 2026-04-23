# database/migrations/script.py.mako

"""add_composite_indexes

Revision ID: f01cfb5f7602
Revises: fd9c5e5b4410
Create Date: 2026-02-18 03:24:33.425071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f01cfb5f7602'
down_revision: Union[str, None] = 'fd9c5e5b4410'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Имя FK `trades.broker_account_id → broker_accounts.id`.
# Указываем явно, чтобы не полагаться на anonymous-FK (SQLite их не умеет
# дропать по None-имени).
_TRADES_BROKER_FK = "trades_broker_account_id_fkey"

# Все ALTER-операции обёрнуты в `batch_alter_table`, чтобы миграция
# работала и на PostgreSQL (native ALTER), и на SQLite (copy-and-move):
# SQLite не поддерживает ALTER CONSTRAINT / DROP CONSTRAINT напрямую.


def upgrade() -> None:
    # ── broker_accounts: новый индекс + уникальный ключ ──
    op.create_index(
        "ix_user_broker", "broker_accounts", ["user_id", "broker_name"], unique=False
    )
    with op.batch_alter_table("broker_accounts") as batch_op:
        batch_op.create_unique_constraint(
            "uq_user_account_name", ["user_id", "account_name"]
        )

    # ── ticket_messages / tickets: смена TIMESTAMP → DateTime(timezone=True) ──
    with op.batch_alter_table("ticket_messages") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )

    # ── trades: новый nullable-столбец broker_account_id + составной индекс + FK ──
    with op.batch_alter_table("trades") as batch_op:
        batch_op.add_column(sa.Column("broker_account_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_user_status", ["user_id", "status"], unique=False)
        batch_op.create_foreign_key(
            _TRADES_BROKER_FK,
            "broker_accounts",
            ["broker_account_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ── users: unique на nickname через индекс, новый индекс на referrer_id ──
    #
    # `UniqueConstraint('nickname')` в complete_init был anonymous — на
    # PostgreSQL он получает имя `users_nickname_key` автоматически, на SQLite
    # — не получает вовсе. Чтобы batch_alter_table мог его найти и дропнуть,
    # передаём `naming_convention` (стандартный шаблон SQLAlchemy).
    _naming_convention = {"uq": "%(table_name)s_%(column_0_name)s_key"}
    with op.batch_alter_table("users", naming_convention=_naming_convention) as batch_op:
        batch_op.drop_constraint("users_nickname_key", type_="unique")
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=True)
    op.create_index(op.f("ix_users_referrer_id"), "users", ["referrer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_referrer_id"), table_name="users")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint(op.f("users_nickname_key"), ["nickname"])

    with op.batch_alter_table("trades") as batch_op:
        batch_op.drop_constraint(_TRADES_BROKER_FK, type_="foreignkey")
        batch_op.drop_index("ix_user_status")
        batch_op.drop_column("broker_account_id")

    with op.batch_alter_table("tickets") as batch_op:
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
    with op.batch_alter_table("ticket_messages") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("broker_accounts") as batch_op:
        batch_op.drop_constraint("uq_user_account_name", type_="unique")
    op.drop_index("ix_user_broker", table_name="broker_accounts")