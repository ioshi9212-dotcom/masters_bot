# Telegram-бот для записи (мастер ↔ клиент)

Новый проект с нуля на **Python + aiogram 3 + SQLite**.

## Что уже реализовано

- чистая модульная структура под Railway;
- SQLite-схема со всеми ключевыми таблицами (`masters`, `clients`, `appointments`, `free_windows`, `waitlist` и др.);
- базовый `/start` flow с выбором роли;
- проверка существующего мастера/клиента по `telegram_id`;
- FSM-регистрация мастера (имя, фамилия, профессии, ДР, старт в сфере, телефон, адрес);
- автоматическая генерация уникального `master_code`;
- базовое меню клиента и создание профиля клиента через FSM;
- подготовлены модули для booking/windows/notifications/statistics/birthdays.

## Структура

- `bot.py` — точка входа
- `config.py` — конфигурация и пути `/data`
- `database/` — база данных и SQL-схема
- `handlers/` — обработчики команд и меню
- `keyboards/` — reply/inline клавиатуры
- `services/` — бизнес-сервисы (каркас)
- `states/` — FSM состояния
- `utils/` — форматирование и работа с датами

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="<telegram-bot-token>"
python bot.py
```

## Railway / Volume

По умолчанию проект использует:

- база: `/data/bot.db`
- резервные копии: `/data/backups/`

Можно переопределить env-переменными:

- `DATA_DIR`
- `DB_PATH`
- `BACKUPS_DIR`
