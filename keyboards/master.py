from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MASTER_MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✍️ Записать клиента"), KeyboardButton(text="📅 Посмотреть записи")],
        [KeyboardButton(text="🕒 Свободные окна"), KeyboardButton(text="⏳ Лист ожидания")],
        [KeyboardButton(text="👤 Кабинет мастера")],
        [KeyboardButton(text="👤 Меню клиента")],
    ],
    resize_keyboard=True,
)


MASTER_EXISTS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Оставить профиль")],
        [KeyboardButton(text="🗑 Удалить и создать новый")],
    ],
    resize_keyboard=True,
)


MASTER_BOOKING_ENTRY_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Мои клиенты"), KeyboardButton(text="➕ Добавить клиента")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_CLIENTS_TOP_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать клиента"), KeyboardButton(text="🗑 Удалить клиента")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_APPOINTMENTS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗑 Удалить запись"), KeyboardButton(text="🗑 Удалить все записи")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_WINDOWS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить окно"), KeyboardButton(text="🗑 Удалить окно")],
        [KeyboardButton(text="🗑 Удалить все окна")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


WINDOWS_PICK_DATE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True,
)


WINDOWS_WORK_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Готово")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_WAITLIST_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Ближайшие окна"), KeyboardButton(text="🗓 Определенная дата")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_CABINET_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Прайс"), KeyboardButton(text="✂️ Услуги")],
        [KeyboardButton(text="👤 Профиль мастера"), KeyboardButton(text="⚙️ Настройки записи")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)


MASTER_SERVICES_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить услугу"), KeyboardButton(text="📋 Мои услуги")],
        [KeyboardButton(text="🗑 Удалить услугу")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


# 🔥 ВОТ ЭТОГО У ТЕБЯ НЕ ХВАТАЛО (из-за него была ошибка)
MASTER_SERVICES_LIST_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать стоимость")],
        [KeyboardButton(text="🗑 Удалить услугу")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


MASTER_PROFILE_EDIT_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Имя"), KeyboardButton(text="👤 Фамилия")],
        [KeyboardButton(text="📱 Телефон"), KeyboardButton(text="💼 Профессии")],
        [KeyboardButton(text="🎂 Дата рождения"), KeyboardButton(text="📅 Начало работы в сфере")],
        [KeyboardButton(text="📍 Адрес работы")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)


MASTER_PROFILE_VIEW_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать профиль")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)


MASTER_SETTINGS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏱ Шаг времени"), KeyboardButton(text="🌅 Начало первой записи")],
        [KeyboardButton(text="🌙 Конец последней записи"), KeyboardButton(text="📆 Записи вперед")],
        [KeyboardButton(text="⌛ Длительность записи мастером")],
        [KeyboardButton(text="⛔ Ограничение записи для клиентов")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)


MASTER_STATS_PERIOD_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Неделя"), KeyboardButton(text="Месяц"), KeyboardButton(text="Год")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)
