# handlers/clients/filter_client.py
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.clients.view_clients import show_clients_page

# Кнопки выбора значения фильтра
def filter_values_kb(filter_type: str):
    kb = InlineKeyboardMarkup(row_width=2)
    if filter_type == "segment":
        kb.add(
            InlineKeyboardButton("VIP", callback_data="filter_apply|segment|VIP"),
            InlineKeyboardButton("Regular", callback_data="filter_apply|segment|Regular"),
            InlineKeyboardButton("New", callback_data="filter_apply|segment|new"),  # вот новый сегмент
            InlineKeyboardButton("Сбросить", callback_data="filter_apply|none|none")
        )
    elif filter_type == "date":
        kb.add(
            InlineKeyboardButton("Сегодня", callback_data="filter_apply|date|today"),
            InlineKeyboardButton("За неделю", callback_data="filter_apply|date|week"),
            InlineKeyboardButton("За месяц", callback_data="filter_apply|date|month"),
            InlineKeyboardButton("Сбросить", callback_data="filter_apply|none|none")
        )
    return kb

# Начало фильтрации: выбираем тип фильтра
async def start_filter_client(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🗓 По дате добавления", callback_data="filter_select|date"),
        InlineKeyboardButton("📊 По сегментации", callback_data="filter_select|segment"),
        InlineKeyboardButton("❌ Без фильтра", callback_data="filter_apply|none|none")
    )
    await callback.message.edit_reply_markup(reply_markup=kb)

# Пользователь выбрал тип фильтра
async def select_filter_type(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    filter_type = callback.data.split("|")[1]
    kb = filter_values_kb(filter_type)
    await callback.message.edit_reply_markup(reply_markup=kb)

# Пользователь выбрал конкретное значение фильтра
async def apply_filter_value(callback: types.CallbackQuery):
    await callback.answer(cache_time=1)
    _, filter_type, filter_value = callback.data.split("|")

    if filter_type == "none":
        filter_by = ""
    else:
        filter_by = f"{filter_type}|{filter_value}"

    await show_clients_page(callback.message, page=1, search_name="", filter_by=filter_by)

# Регистрация всех обработчиков фильтра
def register_filter_clients(dp: Dispatcher):
    dp.register_callback_query_handler(start_filter_client, text="client_filter")
    dp.register_callback_query_handler(select_filter_type, lambda c: c.data.startswith("filter_select|"))
    dp.register_callback_query_handler(apply_filter_value, lambda c: c.data.startswith("filter_apply|"))
