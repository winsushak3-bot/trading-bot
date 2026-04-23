"""add_screener_signals

Revision ID: 58ce57c6041f
Revises: 21342f0f3013
Create Date: 2026-04-12 13:35:04.773917

Создаёт таблицу `screener_signals` для хранения сигналов screener'а.
Ранее таблица существовала только через `Base.metadata.create_all(...)`
в `bot/main.py` — что оставляло чистый PostgreSQL без таблицы после
`alembic upgrade head` и ломало screener.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '58ce57c6041f'
down_revision: Union[str, None] = '21342f0f3013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Cross-dialect JSON: PostgreSQL → JSONB, остальные → JSON.
# Совпадает с типом, используемым в shared/database/models/signals.py.
_JsonType = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "screener_signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        # Уникальный человекочитаемый идентификатор сигнала (#EURUSD_L_a3f2).
        sa.Column("signal_id", sa.String(length=30), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),  # LONG / SHORT
        sa.Column("strength", sa.String(length=10), nullable=False),   # STRONG / MEDIUM / WEAK
        # Оценка уверенности сигнала.
        sa.Column("score", sa.Float(), nullable=False),
        # Уровни входа/выхода.
        sa.Column("entry", sa.Float(), nullable=False),
        sa.Column("stop_loss", sa.Float(), nullable=False),
        sa.Column("take_profit", sa.Float(), nullable=False),
        # Результат (заполняется при закрытии).
        sa.Column("status", sa.String(length=10), nullable=False),     # active / tp_hit / sl_hit
        sa.Column("close_price", sa.Float(), nullable=True),
        sa.Column("pnl_pct", sa.Float(), nullable=True),
        # Telegram-связи.
        sa.Column("message_id", sa.Integer(), nullable=True),
        # v5-метаданные.
        sa.Column("adx", sa.Float(), nullable=True),
        sa.Column("htf_trend", sa.String(length=10), nullable=True),
        # Разбивка по индикаторам.
        sa.Column("details", _JsonType, nullable=True),
        # Таймстемпы сигнала.
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        # Общие created_at/updated_at из Base.
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Индексы — из model __table_args__ и свойств signal_id (unique + index).
    op.create_index(
        op.f("ix_screener_signals_signal_id"),
        "screener_signals",
        ["signal_id"],
        unique=True,
    )
    op.create_index("ix_screener_status", "screener_signals", ["status"], unique=False)
    op.create_index("ix_screener_symbol", "screener_signals", ["symbol"], unique=False)
    op.create_index("ix_screener_opened", "screener_signals", ["opened_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_screener_opened", table_name="screener_signals")
    op.drop_index("ix_screener_symbol", table_name="screener_signals")
    op.drop_index("ix_screener_status", table_name="screener_signals")
    op.drop_index(op.f("ix_screener_signals_signal_id"), table_name="screener_signals")
    op.drop_table("screener_signals")