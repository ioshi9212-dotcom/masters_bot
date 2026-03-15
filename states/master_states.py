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


class MasterAppointmentsState(StatesGroup):
    viewing = State()
    delete_pick_date = State()
    delete_pick_item = State()
    delete_confirm_all = State()


class MasterWindowsState(StatesGroup):
    viewing = State()
    add_pick_date = State()
    add_pick_time = State()
    delete_pick_date = State()
    delete_pick_time = State()
    delete_confirm_all = State()


class MasterCabinetState(StatesGroup):
    menu = State()
    price_edit_pick_service = State()
    price_edit_enter_value = State()
    services_menu = State()
    service_add_name = State()
    service_add_description = State()
    service_add_duration = State()
    service_add_price = State()
    service_delete_pick = State()
    service_delete_confirm = State()
    profile_edit_menu = State()
    profile_edit_name = State()
    profile_edit_last_name = State()
    profile_edit_phone = State()
    profile_edit_birth_date = State()
    profile_edit_work_start = State()
    profile_edit_address = State()
    profile_edit_professions = State()
    settings_menu = State()
    settings_step = State()
    settings_first_time = State()
    settings_last_time = State()
    settings_range = State()
    settings_duration = State()
    settings_limit = State()
