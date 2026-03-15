from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

START_ROLE_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="👩‍🎨 Мастер"), KeyboardButton(text="👤 Клиент")]],
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
