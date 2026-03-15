from aiogram.fsm.state import State, StatesGroup


class MasterRegistrationState(StatesGroup):
    first_name = State()
    last_name = State()
    profession = State()
    birth_date = State()
    work_start = State()
    phone = State()
    address = State()
