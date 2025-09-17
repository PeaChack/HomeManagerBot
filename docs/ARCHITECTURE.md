## Домашний менеджер (Telegram-бот) — Архитектура, план и расширяемость

### Цели и принципы
- **Простота запуска**: один контейнер или `venv`, минимальные зависимости.
- **Мульти-арендность (семьи)**: полная изоляция данных по семьям.
- **Расширяемость**: новые модули (фичи) подключаются без правок ядра.
- **Надёжность**: транзакционная запись, идемпотентность обработчиков.
- **Удобство UX**: клавиатуры, чек-листы, минимум свободного текста.

### Технологический стек (предлагаемый)
- Язык: **Python 3.11+**
- Telegram: **aiogram v3** (современная архитектура, FSM, middlewares)
- Хранилище: **SQLite** для MVP → **PostgreSQL** (prod)
- ORM: **SQLAlchemy 2.x** (или **SQLModel** поверх него)
- Миграции: **Alembic**
- Планировщик: **APScheduler** (reminders/cron)
- Логирование: стандартный `logging` + JSON формат для прод
- Контейнеризация: `Docker` (по желанию)
- Тесты: `pytest`

### Структура проекта (скелет)
```
HomeManagerBot/
├─ app/
│  ├─ bot/                # инициализация aiogram, роутеры, middlewares
│  │  ├─ routers/
│  │  │  ├─ core.py       # старт, помощь, профиль, выбор семьи
│  │  │  ├─ shopping.py   # список покупок
│  │  │  ├─ meals.py      # блюда, меню по дням, чек-листы наличия
│  │  │  ├─ pantry.py     # (расширение) склад/запасы
│  │  │  ├─ chores.py     # (расширение) дела/дежурства
│  │  ├─ keyboards/
│  │  ├─ middlewares/
│  │  ├─ filters/
│  ├─ domain/             # сущности, сервисы, политики
│  │  ├─ models.py
│  │  ├─ services/
│  │  │  ├─ shopping_service.py
│  │  │  ├─ meals_service.py
│  │  ├─ rules/
│  ├─ infrastructure/
│  │  ├─ db/
│  │  │  ├─ base.py       # engine, sessionmaker
│  │  │  ├─ repositories/
│  │  │  │  ├─ shopping_repo.py
│  │  │  │  ├─ meals_repo.py
│  │  ├─ migrations/
│  │  ├─ schedulers/
│  ├─ core/
│  │  ├─ settings.py      # pydantic Settings (токен, БД и т.п.)
│  │  ├─ di.py            # сборка зависимостей
│  │  ├─ plugins.py       # регистрация фич-модулей
│  ├─ utils/
│  └─ main.py
├─ docs/
│  └─ ARCHITECTURE.md
├─ tests/
├─ pyproject.toml / requirements.txt
└─ .env.example
```

### Модель мульти-арендности (семьи)
- Пользователь (Telegram `user_id`) может состоять в нескольких семьях.
- Все записи (покупки, блюда, меню) принадлежат конкретной семье (`family_id`).
- Активная семья выбирается пользователем командой или меню (сохраняется в профиле).
- Права: владелец семьи и обычные участники (минимально для MVP). Позже — роли.

### Ключевые сущности (MVP)
- `Family`: id, name, created_at
- `User`: id (tg_user_id), first_name, last_name, username
- `FamilyMember`: family_id, user_id, role
- `ShoppingItem`: id, family_id, title, qty, unit, is_done, created_by, created_at
- `Dish`: id, family_id, title, instructions?, created_by   (блюда строго внутри семьи)
- `DishIngredient`: id, dish_id, title, qty, unit (нормализуем позже)
- `PlannedMeal`: id, family_id, date (date), dish_id, notes
- `PantryItem` (расширение): id, family_id, product_id, qty, unit, updated_at

Отношения:
- Family 1—N FamilyMember, 1—N ShoppingItem, 1—N Dish, 1—N PlannedMeal
- Dish 1—N DishIngredient
- User N—M Family (через FamilyMember)

### Поведение и сценарии (MVP)
1) Список покупок:
   - Добавить позицию (+qty, unit), отметить как куплено, удалить/очистить.
   - Просмотр чек-листом с инлайн-кнопками.
2) Блюда и меню:
   - Пользователи добавляют блюда и ингредиенты.
   - Планирование меню на даты (календарь/кнопки).
   - Для выбранного блюда запускается чек-лист наличия ингредиентов:
     - «Есть дома», «Нет» → отсутствующее автоматически → в список покупок.

### Идеи для расширений
- Напоминания о покупках, планах меню (утром/накануне).
- Склад/запасы: минимальные остатки, авто-добавление в покупки при снижении.
- Дежурства/дела по дому: график, ротации, статистика.
- Импорт/экспорт CSV/Google Sheets.
- Распознавание чеков (OCR), авто-разбор покупок.
- Роли и права: админ/редактор/читатель на семью.
- Интеграции: календарь (Google), голосовые команды.
- Мультиязычность (i18n) — ru/en.
- Напоминания с гибким расписанием per-пользователь (в рамках семьи).

### Архитектурные решения
- Слоистая архитектура: `bot` (UI) → `domain.services` (бизнес-логика) → `infrastructure.repositories` (БД)
- Обработчики `aiogram` тонкие: парсят апдейт, вызывают сервис, рендерят ответ.
- Сервисы идемпотентны, валидируют вход, работают в транзакции (UnitOfWork).
- Репозитории инкапсулируют SQL/ORM модели.
- Валидация и DTO — через Pydantic (опционально на границах).

### Расширяемость/плагины
- Каждый модуль-фича — самостоятельный пакет с:
  - роутером `aiogram.Router`
  - своими моделями/репозиториями/сервисами
  - регистрацией через `core/plugins.py` (реестр фич)
- Минимальный интерфейс плагина:
  - `def register_routers(dp_or_app): ...`
  - `def register_dependencies(container): ...`
  - `def register_migrations(): ...` (необязательно)
- Новая фича подключается добавлением её в список активных плагинов в настройках.

### Навигация и UX (через клавиатуры)
- Главное меню: «Семья», «Покупки», «Меню», «Блюда».
- Внутри: инлайн-кнопки действий; минимизация свободного текста.
- FSM для длинных диалогов (создание блюда, пошаговый ввод ингредиентов).

### Ошибки и устойчивость
- Centralized error handler middleware: логирование, user-friendly сообщения.
- Идемпотентность по `update_id`/`callback` для критических операций.
- Ограничение гонок: транзакции + уникальные индексы (например, один PlannedMeal на дату/семью/приёмы).

### Хранилище и миграции
- Начать с SQLite (файл) для простоты, один `engine`.
- Alembic миграции с автогенерацией, отдельные ревизии по фичам.
- Переход на PostgreSQL — сменой строки подключения; избегать SQLite-специфичных SQL.

### Планировщик
- APScheduler (BackgroundScheduler) для напоминаний.
- Расписание хранится per-пользователь: каждый участник семьи выбирает время/выключает.
- Хранить задания в БД (позже) или пересоздавать при старте.

### Тестирование
- Юнит-тесты сервисов (бизнес-логика без Telegram).
- Интеграционные — на in-memory SQLite.
- Моки Telegram API (aiogram тестовые утилиты).

### MVP: команды и экраны
- `/start`, выбор/создание семьи.
- Покупки: список, добавить, отметить, очистить.
- Блюда: список, создать, редактировать, удалить.
- Меню: выбрать дату, добавить блюдо на день, чек-лист наличия → недостающее в покупки.

### Мини-ERD (словами)
- Family (1) — (N) FamilyMember — (N) User
- Family (1) — (N) ShoppingItem
- Family (1) — (N) Dish — (N) DishIngredient
- Family (1) — (N) PlannedMeal — (1) Dish

### Пример таблиц (SQL, укорочено)
```sql
CREATE TABLE family (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY,              -- Telegram user_id
  first_name TEXT,
  last_name TEXT,
  username TEXT
);

CREATE TABLE family_member (
  family_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  role TEXT NOT NULL DEFAULT 'member',
  PRIMARY KEY (family_id, user_id)
);

CREATE TABLE shopping_item (
  id INTEGER PRIMARY KEY,
  family_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  qty REAL,
  unit TEXT,
  is_done BOOLEAN NOT NULL DEFAULT 0,
  created_by INTEGER,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dish (
  id INTEGER PRIMARY KEY,
  family_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  instructions TEXT,
  created_by INTEGER
);

CREATE TABLE dish_ingredient (
  id INTEGER PRIMARY KEY,
  dish_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  qty REAL,
  unit TEXT
);

CREATE TABLE planned_meal (
  id INTEGER PRIMARY KEY,
  family_id INTEGER NOT NULL,
  date DATE NOT NULL,
  dish_id INTEGER NOT NULL,
  notes TEXT
);
```

### Безопасность и приватность
- Разграничение по `family_id` на уровне запросов/репозиториев.
- Минимум персональных данных; опционально очистка username.
- Бэкапы БД (при прод) и шифрование секретов (`.env`).

### Настройки и конфигурация
- `Settings` через Pydantic (все через переменные окружения): `BOT_TOKEN`, `DB_URL`, `TIMEZONE`, `LOG_LEVEL`, флаги фич. Пример в `env.example` (переименовать в `.env`).
- Профиль пользователя: текущая активная семья, предпочтения языка/часового пояса.

### Дорожная карта
1. MVP (1–2 недели):
   - Скелет проекта, БД, миграции, стартовые команды.
   - Список покупок (полный цикл).
   - Блюда + ингредиенты.
   - Планирование меню + чек-лист → автодобавление в покупки.
2. Качество жизни:
   - Напоминания, быстрые кнопки, «очистить купленное», пагинация списков.
   - Импорт/экспорт CSV.
3. Расширения:
   - Склад/запасы с минимальными остатками.
   - Дежурства/расписание уборок.
   - Роли и права.
4. Интеграции и ML:
   - OCR чеков, интеграции с календарём/таск-менеджерами.

### Открытые вопросы
1. Единицы измерения: оставить свободный текст сейчас, справочник позже?
2. Планирование меню: поддержать несколько приёмов пищи или оставить один слот?
3. Нужны ли импорт/экспорт и какие форматы в первую очередь (CSV/Sheets)?


