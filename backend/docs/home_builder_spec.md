# Спецификация Конструктора Главной Страницы (Home Builder)

## 1. База Данных (SQLAlchemy)

Таблица `home_tiles`

- `id`: Integer, Primary Key
- `type`: String (enum: 'banner', 'market_overview', 'balance_action', 'quick_trade', 'custom_content') - Тип плиты.
- `size`: String (enum: 'full', 'half') - Ширина плиты. `full` - на всю ширину (col-span-2), `half` - на половину (col-span-1).
- `order`: Integer - Порядок сортировки (для отображения на клиенте).
- `is_active`: Boolean - Активна ли плита.
- `content`: JSONB - Произвольный контент в зависимости от типа (заголовок, текст, картинка, видео, ссылка на действие).

**Пример `content` для `custom_content`**:
```json
{
  "title": "Новое обновление!",
  "description": "Мы добавили новые функции в торгового бота.",
  "image_url": "https://example.com/image.png",
  "action_type": "open_modal",
  "action_payload": "Здесь более длинный текст для модального окна или ссылка на видео..."
}
```

## 2. API Endpoints (FastAPI)

### Публичное API (Для WebApp)
- `GET /api/home/layout`
  - Возвращает список активных плит, отсортированных по `order`.
  - Формат: `[ { id, type, size, content, order } ]`

### Админское API (Для Admin WebApp)
- `GET /api/admin/home/layout` - Все плиты (включая неактивные)
- `POST /api/admin/home/layout` - Создать новую плиту
- `PUT /api/admin/home/layout/{id}` - Обновить плиту (изменить контент, размер, статус)
- `DELETE /api/admin/home/layout/{id}` - Удалить плиту
- `POST /api/admin/home/layout/reorder` - Массовое обновление порядка сортировки (принимает `[{id: 1, order: 0}, {id: 2, order: 1}]`)

## 3. UI (Admin WebApp)
- Раздел в боковом меню: "Конструктор".
- Список плит с возможностью Drag-n-Drop.
- Форма редактирования JSON-контента и загрузки медиа.

## 4. UI (WebApp)
- Файл `HomeView.tsx`.
- Динамический рендер: `layout.map(tile => <TileRenderer data={tile} />)`.
- Учет `col-span-1` (half) и `col-span-2` (full) для правильной CSS-сетки.