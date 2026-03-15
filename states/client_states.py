from aiogram.fsm.state import State, StatesGroup


class ClientProfileState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()
