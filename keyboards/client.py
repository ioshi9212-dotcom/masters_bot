from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CLIENT_MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="✍️ Записаться")],
        [KeyboardButton(text="🕒 Посмотреть свободные окна")],
        [KeyboardButton(text="💅 Какой маникюр сделать?"), KeyboardButton(text="👩‍🎨 Мои мастера")],
        [KeyboardButton(text="⏳ Лист ожидания")],
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
