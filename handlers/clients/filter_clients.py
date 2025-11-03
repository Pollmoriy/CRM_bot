from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.clients.view_clients import show_clients_page


async def start_filter_client(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🗓 По дате добавления", callback_data="filter_date"),
        InlineKeyboardButton("📊 По сегментации", callback_data="filter_segment"),
        InlineKeyboardButton("❌ Без фильтра", callback_data="filter_none")
    )
    await callback.message.answer("Выберите тип фильтрации:", reply_markup=kb)


async def apply_filter(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    filter_map = {
        "filter_date": "date",
        "filter_segment": "segment",
        "filter_none": ""
    }
    filter_by = filter_map.get(callback.data, "")
    await state.update_data(filter_by=filter_by)

    data = await state.get_data()
    search_name = data.get("search_name", "")

    await show_clients_page(callback.message, search_name, filter_by, page=1)


def register_filter_clients(dp: Dispatcher):
    dp.register_callback_query_handler(start_filter_client, text="filter_client")
    dp.register_callback_query_handler(apply_filter, text_startswith="filter_")
