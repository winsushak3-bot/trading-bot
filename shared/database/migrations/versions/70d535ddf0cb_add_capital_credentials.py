# database/migrations/versions/70d535ddf0cb_add_capital_credentials.py

"""add_capital_credentials (PLACEHOLDER — no-op)

Revision ID: 70d535ddf0cb
Revises: 8a6cb9793124
Create Date: 2026-01-28 00:25:53.237231

⚠️  Это no-op миграция, оставленная для сохранения целостности цепочки ревизий.

Хранение Capital.com-кредов было вынесено в отдельную модель `BrokerAccount`
(ревизия `fd9c5e5b4410_add_broker_accounts.py`), а эта ревизия осталась
как исторический мостик. На прод-базах, где она уже применена, удалять её
нельзя — сломается `alembic_version`. Поэтому оставляем пустой.
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401  (оставлено для шаблонной совместимости)
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '70d535ddf0cb'
down_revision: Union[str, None] = '8a6cb9793124'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op placeholder — см. docstring выше."""
    pass


def downgrade() -> None:
    """No-op placeholder — см. docstring выше."""
    pass