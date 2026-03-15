from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

MASTER_DELETE_CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

CONFIRM_DELETE_CLIENT_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
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

MASTER_CONFIRM_DELETE_SERVICE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить")],
        [KeyboardButton(text="◀️ Отмена"), KeyboardButton(text="🏠 Главное меню")],
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
