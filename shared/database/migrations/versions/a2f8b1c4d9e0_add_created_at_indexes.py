"""add_created_at_indexes

Revision ID: a2f8b1c4d9e0
Revises: 58ce57c6041f
Create Date: 2026-04-16 20:40:00.000000

Индексы для часто выполняемых запросов сортировки/фильтрации по датам:
- trades.created_at  — «последние сделки».
- tickets.(status, updated_at)  — get_tickets_by_status в админке.
- tickets.created_at  — общая сортировка.
- ticket_messages.(ticket_id, created_at) — история переписки тикета.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "a2f8b1c4d9e0"
down_revision: Union[str, None] = "58ce57c6041f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_trades_created_at", "trades", ["created_at"], unique=False)
    op.create_index(
        "ix_tickets_status_updated", "tickets", ["status", "updated_at"], unique=False
    )
    op.create_index("ix_tickets_created_at", "tickets", ["created_at"], unique=False)
    op.create_index(
        "ix_ticket_messages_ticket_created",
        "ticket_messages",
        ["ticket_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ticket_messages_ticket_created", table_name="ticket_messages")
    op.drop_index("ix_tickets_created_at", table_name="tickets")
    op.drop_index("ix_tickets_status_updated", table_name="tickets")
    op.drop_index("ix_trades_created_at", table_name="trades")
