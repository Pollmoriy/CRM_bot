from aiogram.dispatcher.filters.state import State, StatesGroup

class AddClientFSM(StatesGroup):
    full_name = State()
    phone = State()
    telegram = State()
    birth_date = State()
    segment = State()
    notes = State()
