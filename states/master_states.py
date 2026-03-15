from aiogram.fsm.state import State, StatesGroup


class MasterRegistrationState(StatesGroup):
    first_name = State()
    last_name = State()
    profession = State()
    birth_date = State()
    work_start = State()
    phone = State()
    address = State()


class MasterDeleteProfileState(StatesGroup):
    confirm = State()


class MasterClientsState(StatesGroup):
    viewing = State()


class MasterClientCreateState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()


class MasterClientEditState(StatesGroup):
    select_client = State()
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()


class MasterClientDeleteState(StatesGroup):
    select_client = State()
    confirm = State()
