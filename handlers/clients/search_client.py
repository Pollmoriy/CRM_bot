# handlers/clients/search_client.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp
from handlers.clients.view_clients import show_clients_page

class SearchClientStates(StatesGroup):
    waiting_for_name = State()

async def start_search_client(callback: types.CallbackQuery):
    # Быстрый ack
    await callback.answer(cache_time=1)
    # Запускаем FSM: попросим имя
    await callback.message.answer("Введите имя или часть имени для поиска:")
    await SearchClientStates.waiting_for_name.set()

@dp.message_handler(state=SearchClientStates.waiting_for_name)
async def process_search_name(message: types.Message, state: FSMContext):
    search_text = message.text.strip()
    if not search_text:
        await message.answer("Пустой запрос. Введите имя или часть имени:")
        return

    # Сохраним в state (если надо) или сразу покажем результаты (страница 1)
    await state.update_data(search_name=search_text)
    # Показываем страницу 1 с этим поиском
    await show_clients_page(message, page=1, search_name=search_text, filter_by="")
    await state.finish()
