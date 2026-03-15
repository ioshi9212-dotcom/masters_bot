from aiogram.fsm.state import State, StatesGroup


class ClientProfileState(StatesGroup):
    create_first_name = State()
    create_last_name = State()
    create_phone = State()
    create_birth_date = State()
    edit_pick_field = State()
    edit_first_name = State()
    edit_last_name = State()
    edit_phone = State()
    edit_birth_date = State()
    delete_confirm = State()


class ClientBookingState(StatesGroup):
    pick_master = State()
    enter_master_code = State()
    pick_service = State()
    pick_date = State()
    pick_time = State()


class ClientMastersState(StatesGroup):
    pick_master = State()
    first_name = State()
    last_name = State()
    phone = State()
    birth_date = State()
