# handlers/deals/search_deals.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from loader import dp, safe_answer
from handlers.deals.view_deals import show_deals


class SearchDealStates(StatesGroup):
    waiting_for_name = State()


async def start_search_deal(callback: types.CallbackQuery):
    await safe_answer(callback)
    # Просим ввести текст (без клавиатуры)
    try:
        await callback.message.answer("Введите название сделки:", reply_markup=None)
    except Exception:
        await callback.answer("Введите название сделки:")
    await SearchDealStates.waiting_for_name.set()


@dp.message_handler(state=SearchDealStates.waiting_for_name)
async def process_search_name(message: types.Message, state: FSMContext):
    search_text = message.text.strip()
    if not search_text:
        await message.answer("Пустой запрос. Введите название сделки:")
        return

    # Показываем результаты поиска (show_deals умеет принимать Message)
    await show_deals(message, page=1, search_name=search_text, filter_by="")
    await state.finish()
