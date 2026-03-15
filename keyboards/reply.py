from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


START_ROLE_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="👩‍🎨 Мастер"), KeyboardButton(text="👤 Клиент")]],
    resize_keyboard=True,
)

MASTER_MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✍️ Записать клиента"), KeyboardButton(text="📅 Посмотреть записи")],
        [KeyboardButton(text="🕒 Свободные окна"), KeyboardButton(text="⏳ Лист ожидания")],
        [KeyboardButton(text="👤 Кабинет мастера")],
        [KeyboardButton(text="👤 Режим клиента")],
    ],
    resize_keyboard=True,
)

CLIENT_MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="✍️ Записаться")],
        [KeyboardButton(text="🕒 Посмотреть свободные окна")],
        [KeyboardButton(text="💅 Какой маникюр сделать?"), KeyboardButton(text="👩‍🎨 Мои мастера")],
        [KeyboardButton(text="⏳ Лист ожидания")],
    ],
    resize_keyboard=True,
)

YES_SKIP_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ Пропустить")]],
    resize_keyboard=True,
)

SKIP_BACK_HOME_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏭ Пропустить")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

PROFESSION_DONE_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Готово")]],
    resize_keyboard=True,
)

MASTER_EXISTS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Оставить профиль")],
        [KeyboardButton(text="🗑 Удалить и создать новый")],
    ],
    resize_keyboard=True,
)

MASTER_DELETE_CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
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
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True,
)

CLIENT_PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать профиль"), KeyboardButton(text="🗑 Удалить профиль")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True,
)

CONFIRM_DELETE_CLIENT_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True,
)

MASTER_DELETE_CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🏠 Главное меню")]
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
    keyboard=[[KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]],
    resize_keyboard=True,
)

WINDOWS_WORK_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Готово")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CONFIRM_DELETE_ALL_APPOINTMENTS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить все записи")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CONFIRM_DELETE_ALL_WINDOWS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить все окна")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

MASTER_WAITLIST_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Ближайшие окна"), KeyboardButton(text="📆 Определенная дата")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True,
)

MASTER_BOOKING_ENTRY_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Мои клиенты"), KeyboardButton(text="➕ Добавить клиента")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]
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
        [KeyboardButton(text="➕ Добавить услугу"), KeyboardButton(text="🗑 Удалить услугу")],
MASTER_CLIENTS_TOP_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать клиента"), KeyboardButton(text="🗑 Удалить клиента")],
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

MASTER_CONFIRM_DELETE_SERVICE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
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


CLIENT_PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать профиль"), KeyboardButton(text="🗑 Удалить профиль")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CLIENT_NO_PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Создать профиль")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CLIENT_DELETE_PROFILE_CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Удалить профиль")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CLIENT_EDIT_PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Имя"), KeyboardButton(text="👤 Фамилия")],
        [KeyboardButton(text="📱 Телефон"), KeyboardButton(text="🎂 Дата рождения")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CLIENT_MASTER_MODE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="✍️ Записаться")],
        [KeyboardButton(text="🕒 Посмотреть свободные окна")],
        [KeyboardButton(text="💅 Какой маникюр сделать?"), KeyboardButton(text="👩‍🎨 Мои мастера")],
        [KeyboardButton(text="⏳ Лист ожидания")],
        [KeyboardButton(text="🔁 Вернуться в режим мастера")],
    ],
    resize_keyboard=True,
)

CLIENT_WRITE_MASTER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✉️ Написать мастеру")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)
