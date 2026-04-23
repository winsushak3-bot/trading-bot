"""drop_screener_signals

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-04-18 12:00:00.000000

Удаляет таблицу `screener_signals` — скринер полностью убран из проекта.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Cross-dialect JSON: PostgreSQL → JSONB, остальные → JSON.
_JsonType = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.drop_index("ix_screener_opened", table_name="screener_signals")
    op.drop_index("ix_screener_symbol", table_name="screener_signals")
    op.drop_index("ix_screener_status", table_name="screener_signals")
    op.drop_index(op.f("ix_screener_signals_signal_id"), table_name="screener_signals")
    op.drop_table("screener_signals")


def downgrade() -> None:
    # Re-create the table if rollback is needed
    op.create_table(
        "screener_signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("signal_id", sa.String(length=30), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("strength", sa.String(length=10), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("entry", sa.Float(), nullable=False),
        sa.Column("stop_loss", sa.Float(), nullable=False),
        sa.Column("take_profit", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("close_price", sa.Float(), nullable=True),
        sa.Column("pnl_pct", sa.Float(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.Column("adx", sa.Float(), nullable=True),
        sa.Column("htf_trend", sa.String(length=10), nullable=True),
        sa.Column("details", _JsonType, nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_screener_signals_signal_id"), "screener_signals", ["signal_id"], unique=True)
    op.create_index("ix_screener_status", "screener_signals", ["status"], unique=False)
    op.create_index("ix_screener_symbol", "screener_signals", ["symbol"], unique=False)
    op.create_index("ix_screener_opened", "screener_signals", ["opened_at"], unique=False)
