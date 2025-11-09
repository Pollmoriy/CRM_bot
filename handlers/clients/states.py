from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchClientState(StatesGroup):
    waiting_for_name = State()

class EditClientStates(StatesGroup):
    choose_field = State()  # пользователь выбирает, что редактировать
    enter_new_value = State()