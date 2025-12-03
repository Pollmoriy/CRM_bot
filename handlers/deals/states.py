from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchClientState(StatesGroup):
    waiting_for_name = State()