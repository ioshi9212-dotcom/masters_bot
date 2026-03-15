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

CLIENT_PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать профиль"), KeyboardButton(text="🗑 Удалить профиль")],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
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
