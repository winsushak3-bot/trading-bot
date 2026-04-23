# database/migrations/script.py.mako

"""Add support tables (PLACEHOLDER — no-op)

Revision ID: 20d41c9077bb
Revises: f01cfb5f7602
Create Date: 2026-02-28 10:18:23.183732

⚠️  Это no-op миграция, оставленная для сохранения целостности цепочки ревизий.

Таблицы `tickets` и `ticket_messages`, которые исторически должны были
создаваться здесь, были позднее сквошены в `8a6cb9793124_complete_init.py`
(начальная ревизия). На прод-базах, где эта ревизия уже была применена до
сквоша, удалить её — значит сломать `alembic_version`. Поэтому оставляем
как пустой «мостик».

При деплое на чистую БД ничего не произойдёт — таблицы создадутся в
`complete_init`, а эта ревизия просто отметится в `alembic_version`.
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401  (оставлено для шаблонной совместимости)
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '20d41c9077bb'
down_revision: Union[str, None] = 'f01cfb5f7602'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op placeholder — см. docstring выше."""
    pass


def downgrade() -> None:
    """No-op placeholder — см. docstring выше."""
    pass