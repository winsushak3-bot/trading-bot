# Trading Bot — Полная структура проекта

## Быстрый старт (локально, Windows)

### 1. Зависимости

```powershell
# Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Frontends
cd webapp && npm install && cd ..
cd admin && npm install && cd ..
```

Также нужны локально запущенные **PostgreSQL** и **Redis** — либо через `docker/docker-compose.yml`, либо нативно.

### 2. Конфигурация `.env`

Создайте `.env` в корне проекта. Обязательные переменные:

```env
# Telegram
BOT_TOKEN=<ваш токен от @BotFather>
ADMIN_IDS=[<telegram_id>]
ADMIN_PASSWORD=<пароль для /admin UI>          # используется только в login форме
CHANNEL_ID=<id канала>
CHAT_TOPIC_ID=<id темы в main канале, опционально>

# Storage
DB_URL=postgresql+asyncpg://user:pass@localhost:5432/bot
REDIS_URL=redis://localhost:6379/0

# Capital.com (Demo)
CAPITAL_EMAIL=<email>
CAPITAL_PASSWORD=<пароль>
CAPITAL_API_KEY=<API key>

# Security
ENCRYPTION_KEY=<Fernet key, >= 32 chars>       # для api_key/password брокера в БД

# Webhook (опционально — если задан, бот работает в webhook-режиме через backend)
WEBHOOK_BASE_URL=https://<ваш-ngrok>.ngrok-free.dev
```

### 3. Миграции БД

```powershell
alembic upgrade head
```

### 4. Запуск

**Вариант A — polling (dev):**
```powershell
python -m bot.main                    # бот сам ходит за апдейтами
python -m uvicorn backend.main:app --reload --port 8000
```

**Вариант B — webhook через backend:** задать `WEBHOOK_BASE_URL` в `.env`, затем только backend:
```powershell
python -m uvicorn backend.main:app --port 8000
```

Frontends:
```powershell
cd webapp  && npm run dev             # :5173 (Telegram WebApp)
cd admin   && npm run dev             # :5175 (Admin UI)
```

### 5. Admin UI — авторизация

`/admin` открывается в обычном браузере (не как Telegram WebApp), поэтому авторизация — через `POST /api/admin/auth/login`:
- `telegram_id` должен быть в `ADMIN_IDS`;
- `password` должен совпадать с `ADMIN_PASSWORD` из `.env`.

Сервер возвращает подписанный токен (HMAC-SHA256 на базе `BOT_TOKEN`, TTL 24 часа), фронт хранит его в `sessionStorage` и шлёт как `Authorization: Admin <token>` во всех запросах.

### 6. Тесты

```powershell
pytest -q                             # использует .env.test
```

## Безопасность ключей (после рефакторинга Фаза 1–4)

- `BOT_TOKEN` — никогда не логируется, используется как HMAC-ключ для webhook `secret_token` и admin token.
- `ENCRYPTION_KEY` — Fernet для api_key/password брокеров в БД; минимум 32 символа.
- `ADMIN_PASSWORD` — только серверная проверка (нет в frontend бандле).
- Telegram initData валидируется с `auth_date` freshness (24h) и timing-safe HMAC.
- Webhook endpoint принимает апдейты только при совпадающем `X-Telegram-Bot-Api-Secret-Token`.
- `.env` и `uploads/` исключены из `.gitignore`, `dump.rdb` тоже.

## Структура

```
├── 📁 bot/                                 # 🤖 Telegram бот (aiogram)
│   ├── 📁 handlers/
│   │   ├── 📁 admin/
│   │   │   ├── 📁 keyboards/
│   │   │   │   └── main.py                 # Админские клавиатуры
│   │   │   ├── 📁 management/
│   │   │   │   └── management.py           # Управление пользователями
│   │   │   ├── 📁 service/
│   │   │   │   └── service.py              # Сервисные функции
│   │   │   └── panel.py                    # Панель управления
│   │   ├── 📁 common/
│   │   │   ├── 📁 back/
│   │   │   │   ├── registry.py             # Реестр "назад"
│   │   │   │   └── router.py               # Роутер навигации
│   │   │   ├── 📁 chat_commands/
│   │   │   │   ├── 📁 general/handlers.py  # Общие команды
│   │   │   │   ├── 📁 staff/handlers.py    # Команды персонала
│   │   │   │   ├── 📁 stats/handlers.py    # Статистика
│   │   │   │   ├── 📁 system/handlers.py   # Системные команды
│   │   │   │   ├── 📁 users/handlers.py    # Команды пользователей
│   │   │   │   └── router.py               # Роутер команд
│   │   │   ├── 📁 onboarding/
│   │   │   │   ├── router.py               # Роутер онбординга
│   │   │   │   └── service.py              # Логика онбординга
│   │   │   ├── 📁 start/
│   │   │   │   ├── router.py               # Роутер /start
│   │   │   │   └── service.py              # Логика /start
│   │   │   └── navigation.py               # Навигация
│   │   ├── 📁 keyboards/
│   │   │   ├── common.py                   # Общие клавиатуры
│   │   │   ├── main_menu.py                # Главное меню
│   │   │   ├── profile.py                  # Клавиатуры профиля
│   │   │   └── trading.py                  # Клавиатуры торговли
│   │   ├── 📁 profile/
│   │   │   ├── 📁 feedback/
│   │   │   │   └── feedback.py             # Обратная связь
│   │   │   ├── 📁 referral/
│   │   │   │   ├── 📁 info/info.py         # Инфо о реферальной системе
│   │   │   │   ├── 📁 list/referral_list.py # Список рефералов
│   │   │   │   ├── 📁 wallet/wallet.py     # Кошелек рефералов
│   │   │   │   └── referral.py             # Главная рефералов
│   │   │   ├── 📁 settings/
│   │   │   │   ├── 📁 language/language.py  # Смена языка
│   │   │   │   ├── 📁 nickname/nickname.py  # Смена никнейма
│   │   │   │   ├── 📁 notifications/notifications.py
│   │   │   │   └── settings.py             # Главная настроек
│   │   │   └── profile.py                  # Главное меню профиля
│   │   └── 📁 trading/
│   │       ├── 📁 demo/
│   │       │   ├── connect.py              # Подключение демо
│   │       │   └── demo.py                 # Демо-счет
│   │       ├── 📁 forex/
│   │       │   └── forex.py                # Forex торговля
│   │       └── trading.py                  # Главное меню торговли
│   ├── 📁 middlewares/
│   │   ├── db.py                           # Проброс сессии БД
│   │   ├── i18n.py                         # Интернационализация
│   │   ├── outer.py                        # Логирование, проверки
│   │   └── throttling.py                   # Rate limiting
│   ├── 📁 filters/
│   │   └── localized_text.py               # LocalizedText фильтр
│   ├── 📁 states/
│   │   ├── admin.py                        # FSM: админ
│   │   ├── onboarding.py                   # FSM: онбординг
│   │   ├── profile.py                      # FSM: профиль
│   │   └── trading.py                      # FSM: торговля
│   └── main.py                             # Точка запуска бота
│
├── 📁 backend/                             # 🌐 FastAPI Backend
│   ├── 📁 api/
│   │   ├── 📁 routes/
│   │   │   ├── auth.py                     # Telegram WebApp авторизация
│   │   │   ├── home.py                     # API главной страницы
│   │   │   ├── news.py                     # Контроллер новостей (тонкий)
│   │   │   ├── public.py                   # Публичные эндпоинты
│   │   │   ├── support.py                  # API тикетов поддержки
│   │   │   ├── trading.py                  # Capital.com API endpoints
│   │   │   └── uploads.py                  # Загрузка файлов
│   │   └── 📁 schemas/
│   │       ├── __init__.py                 # Auth, Trading схемы
│   │       ├── home.py                     # Схемы главной страницы
│   │       └── support.py                  # Схемы поддержки
│   ├── 📁 core/
│   │   ├── database.py                     # Настройка БД
│   │   └── 📁 security/
│   │       └── telegram_auth.py            # Валидация Telegram initData
│   ├── 📁 services/
│   │   └── news.py                         # Сервис новостей (RSS + парсер статей)
│   ├── 📁 docs/
│   │   └── home_builder_spec.md            # Спецификация конструктора
│   ├── bot_webhook.py                      # Webhook интеграция бота
│   └── main.py                             # FastAPI приложение + SPA fallback
│
├── 📁 shared/                              # ⚙️ Общий переиспользуемый код
│   ├── 📁 components/
│   │   ├── 📁 trading/
│   │   │   ├── position.py                 # Менеджер позиций
│   │   │   ├── risk.py                     # Калькулятор рисков
│   │   │   ├── signals.py                  # Торговые сигналы
│   │   │   └── validator.py                # Валидаторы торговых данных
│   │   └── i18n.py                         # Интернационализация
│   ├── 📁 database/
│   │   ├── 📁 migrations/
│   │   │   ├── 📁 versions/                # Alembic миграции
│   │   │   ├── env.py
│   │   │   └── script.py.mako
│   │   ├── 📁 models/
│   │   │   ├── accounts.py                 # Брокерские аккаунты
│   │   │   ├── applications.py             # Заявки
│   │   │   ├── audit.py                    # Аудит
│   │   │   ├── base.py                     # Базовая модель
│   │   │   ├── home.py                     # Модели главной страницы
│   │   │   ├── signals.py                  # Модели сигналов
│   │   │   ├── support.py                  # Тикеты поддержки
│   │   │   ├── trades.py                   # Модель сделок
│   │   │   ├── trading.py                  # Торговые модели
│   │   │   └── users.py                    # Пользователи
│   │   ├── 📁 repo/
│   │   │   ├── accounts.py                 # Репозиторий аккаунтов
│   │   │   ├── base.py                     # Базовый репозиторий
│   │   │   ├── home.py                     # Данные главной страницы
│   │   │   ├── signals.py                  # Репозиторий сигналов
│   │   │   ├── support.py                  # Работа с тикетами
│   │   │   ├── trades.py                   # Репозиторий сделок
│   │   │   └── users.py                    # Работа с пользователями
│   │   ├── core.py                         # Конфигурация SQLAlchemy
│   │   └── enums.py                        # Перечисления БД
│   ├── 📁 services/
│   │   ├── capital.py                      # API клиент Capital.com
│   │   └── cryptography.py                 # Шифрование данных (Fernet)
│   ├── 📁 utils/
│   │   ├── decorators.py                   # Декораторы прав доступа
│   │   ├── exceptions.py                   # Кастомные исключения
│   │   ├── logger.py                       # Настройка Loguru
│   │   ├── system_info.py                  # Системные данные
│   │   └── text_format.py                  # Утилиты форматирования
│   ├── 📁 locales/
│   │   ├── en.json
│   │   ├── ru.json
│   │   └── ua.json
│   ├── config.py                           # Pydantic конфигурация
│   └── constants.py                        # Общие константы
│
├── 📁 webapp/                              # 📱 Telegram Mini App (React/Vite)
│   ├── 📁 src/
│   │   ├── 📁 api/
│   │   │   └── client.ts                   # Axios API клиент
│   │   ├── 📁 hooks/
│   │   │   ├── useBackButton.ts            # Кнопка «Назад» Telegram
│   │   │   ├── useNews.ts                  # Хук загрузки новостей + тип NewsArticle
│   │   │   ├── useSmartWallet.ts           # Thirdweb кошелек
│   │   │   ├── useWebApp.ts                # Telegram WebApp API
│   │   │   └── index.ts
│   │   ├── 📁 i18n/
│   │   │   ├── 📁 locales/                 # en.json, ru.json, ua.json
│   │   │   ├── i18n.ts                     # Конфиг i18next
│   │   │   ├── useTranslation.ts           # Хук перевода
│   │   │   └── index.ts
│   │   ├── 📁 lib/
│   │   │   ├── thirdweb.ts                 # Конфиг Thirdweb
│   │   │   └── tokens.ts                   # Токены
│   │   ├── 📁 pages/
│   │   │   ├── 📁 home/
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 ArticleModal/    # Модалка полной статьи
│   │   │   │   │   │   ├── ArticleModal.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 DynamicTiles/    # Динамические плитки (конструктор)
│   │   │   │   │   │   ├── CubeTile.tsx
│   │   │   │   │   │   ├── DynamicTiles.tsx
│   │   │   │   │   │   ├── ExpandBlocks.tsx
│   │   │   │   │   │   ├── TileModal.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 NewsFilter/      # Фильтр категорий новостей
│   │   │   │   │   │   ├── NewsFilter.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 NewsItem/        # Карточка новости
│   │   │   │   │   │   ├── NewsItem.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── HomeView.tsx            # Главная страница
│   │   │   │   └── index.ts
│   │   │   ├── 📁 profile/
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 AboutTile/       # О приложении
│   │   │   │   │   │   ├── AboutModal.tsx
│   │   │   │   │   │   ├── AboutTile.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 NotificationButton/ # Уведомления
│   │   │   │   │   │   ├── NotificationButton.tsx
│   │   │   │   │   │   ├── NotificationModal.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 ProfileCard/     # Карточка профиля
│   │   │   │   │   │   ├── ProfileCard.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── 📁 SettingsTile/    # Настройки
│   │   │   │   │   │   ├── 📁 components/
│   │   │   │   │   │   │   ├── 📁 FullscreenSetting/
│   │   │   │   │   │   │   ├── 📁 LanguageSetting/
│   │   │   │   │   │   │   ├── 📁 ThemeSetting/
│   │   │   │   │   │   │   ├── 📁 TwoFASetting/
│   │   │   │   │   │   │   └── index.ts
│   │   │   │   │   │   ├── SettingsModal.tsx
│   │   │   │   │   │   ├── SettingsTile.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── ProfileView.tsx
│   │   │   │   └── index.ts
│   │   │   ├── 📁 support/                 # Чат с поддержкой
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 ChatTile/        # Плитка чата
│   │   │   │   │   ├── 📁 FAQSection/      # Секция FAQ
│   │   │   │   │   ├── 📁 SupportChat/     # Чат поддержки
│   │   │   │   │   └── index.ts
│   │   │   │   ├── SupportView.tsx
│   │   │   │   └── index.ts
│   │   │   ├── 📁 trade/                   # Торговля (графики, баланс)
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 AnalyticsTile/   # Аналитика
│   │   │   │   │   ├── 📁 CryptoTile/      # Крипто-плитка
│   │   │   │   │   ├── 📁 ForexBalanceTile/ # Баланс форекс
│   │   │   │   │   ├── 📁 ForexTile/       # Форекс-плитка
│   │   │   │   │   ├── 📁 PriceChart/      # График цен
│   │   │   │   │   ├── 📁 StatisticsTile/  # Статистика
│   │   │   │   │   ├── 📁 TradeScreen/     # Экран торговли
│   │   │   │   │   └── index.ts
│   │   │   │   ├── TradeView.tsx
│   │   │   │   └── index.ts
│   │   │   ├── 📁 wallet/                  # Кошелек
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 ActionsCard/     # Карточка действий
│   │   │   │   │   ├── 📁 BalanceCard/     # Карточка баланса
│   │   │   │   │   ├── 📁 TokenList/       # Список токенов
│   │   │   │   │   └── index.ts
│   │   │   │   ├── WalletView.tsx
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── 📁 shared/
│   │   │   ├── 📁 layout/
│   │   │   │   ├── BottomNav.tsx           # Нижняя навигация
│   │   │   │   ├── Header.tsx              # Шапка
│   │   │   │   ├── LoadingScreen.tsx       # Экран загрузки
│   │   │   │   └── index.ts
│   │   │   ├── 📁 ui/
│   │   │   │   ├── PageWrapper.tsx         # Обертка страниц
│   │   │   │   ├── ErrorBoundary.tsx       # Ловец ошибок
│   │   │   │   ├── ImageViewer.tsx         # Полноэкранный просмотр изображений
│   │   │   │   └── index.ts
│   │   │   └── 📁 animations/
│   │   │       ├── variants.ts             # Варианты анимаций Framer Motion
│   │   │       └── index.ts
│   │   ├── 📁 store/
│   │   │   ├── useAppStore.ts              # Основной store
│   │   │   ├── useWalletStore.ts           # Store кошелька
│   │   │   └── index.ts
│   │   ├── 📁 utils/
│   │   │   ├── haptic.ts                   # Тактильная отдача
│   │   │   └── index.ts
│   │   ├── App.tsx                         # Корневой компонент
│   │   ├── main.tsx
│   │   └── index.css                       # Глобальные стили
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── 📁 admin/                               # 🛠️ Админ-панель (React/Vite)
│   ├── 📁 src/
│   │   ├── 📁 api/
│   │   │   └── client.ts                   # API клиент
│   │   ├── 📁 pages/
│   │   │   ├── 📁 constructor/
│   │   │   │   ├── 📁 components/
│   │   │   │   │   ├── 📁 DragGhost/       # Призрак перетаскивания
│   │   │   │   │   ├── 📁 GridTile/        # Плитка в сетке
│   │   │   │   │   ├── 📁 ImageCropModal/  # Кроп изображений
│   │   │   │   │   ├── 📁 ListTile/        # Плитка в списке
│   │   │   │   │   ├── 📁 LivePreview/     # Предпросмотр
│   │   │   │   │   ├── 📁 TileEditor/      # Редактор плитки
│   │   │   │   │   │   ├── TileEditor.tsx
│   │   │   │   │   │   ├── TilePreview.tsx
│   │   │   │   │   │   ├── TabAction.tsx
│   │   │   │   │   │   ├── TabContent.tsx
│   │   │   │   │   │   ├── TabStyle.tsx
│   │   │   │   │   │   ├── constants.ts
│   │   │   │   │   │   ├── types.ts
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── ConstructorView.tsx     # Конструктор главной
│   │   │   │   └── index.ts
│   │   │   ├── 📁 login/
│   │   │   │   ├── LoginView.tsx           # Страница входа
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── 📁 shared/
│   │   │   ├── 📁 layout/
│   │   │   │   ├── AdminBottomNav.tsx      # Навигация
│   │   │   │   └── index.ts
│   │   │   └── 📁 ui/
│   │   │       ├── ToastContainer.tsx      # Уведомления
│   │   │       ├── useToast.ts             # Хук тостов
│   │   │       └── index.ts
│   │   ├── 📁 store/
│   │   │   └── useAdminStore.ts            # Zustand store
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── 📁 docker/                              # 🐳 Docker конфигурация
│   ├── docker-compose.yml                  # Оркестрация контейнеров
│   ├── Dockerfile.bot                      # Образ бота
│   └── Dockerfile.backend                  # Образ backend
│
├── 📁 tests/                               # 🧪 Тестирование (Pytest)
│   ├── 📁 integration/
│   │   └── 📁 database/
│   │       ├── test_accounts_repo.py       # Тесты репозитория аккаунтов
│   │       └── test_users_repo.py          # Тесты репозитория пользователей
│   ├── 📁 unit/
│   │   ├── 📁 components/
│   │   │   ├── test_i18n.py                # Тесты локализации
│   │   │   └── 📁 trading/
│   │   │       ├── test_position.py        # Тесты позиций
│   │   │       ├── test_risk.py            # Тесты рисков
│   │   │       └── test_validator.py       # Тесты валидаторов
│   │   ├── 📁 middlewares/
│   │   │   ├── test_db.py                  # Тесты middleware БД
│   │   │   ├── test_i18n_middleware.py      # Тесты middleware i18n
│   │   │   └── test_outer.py               # Тесты outer middleware
│   │   └── 📁 services/
│   │       ├── test_capital.py             # Тесты Capital.com
│   │       └── test_cryptography.py        # Тесты шифрования
│   ├── conftest.py                         # Фикстуры pytest
│   └── test_setup.py                       # Проверка тестового окружения
│
├── 📁 uploads/                             # Загруженные файлы
├── 📁 logs/                                # Логи приложения
├── .env                                    # Секретные ключи
├── alembic.ini                             # Конфиг миграций
├── pytest.ini                              # Конфиг тестов
├── requirements.txt                        # Python зависимости
├── requirements-test.txt                   # Тестовые зависимости
└── start-wt.bat                            # Скрипт запуска (Windows)
```
