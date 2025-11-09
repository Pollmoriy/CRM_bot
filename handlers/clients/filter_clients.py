# handlers/clients/filter_clients.py
from aiogram import types, Dispatcher
from handlers.clients.view_clients import show_clients_page

def filter_values_kb(filter_type: str):
    kb = types.InlineKeyboardMarkup(row_width=2)
    if filter_type == "segment":
        kb.add(
            types.InlineKeyboardButton("VIP", callback_data="filter_apply|segment|VIP"),
            types.InlineKeyboardButton("Regular", callback_data="filter_apply|segment|Regular"),
            types.InlineKeyboardButton("New", callback_data="filter_apply|segment|New"),
        )
    elif filter_type == "date":
        kb.add(
            types.InlineKeyboardButton("Сегодня", callback_data="filter_apply|date|today"),
            types.InlineKeyboardButton("Последняя неделя", callback_data="filter_apply|date|week"),
            types.InlineKeyboardButton("Последний месяц", callback_data="filter_apply|date|month"),
        )
    kb.add(types.InlineKeyboardButton("❌ Сбросить", callback_data="filter_apply|none|none"))
    return kb


async def start_filter_client(callback: types.CallbackQuery):
    await callback.answer()
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🗓 По дате добавления", callback_data="filter_select|date"),
        types.InlineKeyboardButton("📊 По сегментации", callback_data="filter_select|segment"),
    )
    kb.add(types.InlineKeyboardButton("❌ Без фильтра", callback_data="filter_apply|none|none"))
    await callback.message.edit_reply_markup(reply_markup=kb)


async def select_filter_type(callback: types.CallbackQuery):
    await callback.answer()
    _, filter_type = callback.data.split("|", 1)
    kb = filter_values_kb(filter_type)
    await callback.message.edit_reply_markup(reply_markup=kb)


async def apply_filter_value(callback: types.CallbackQuery):
    await callback.answer()
    _, filter_type, filter_value = callback.data.split("|", 2)
    filter_by = "" if filter_type == "none" else f"{filter_type}|{filter_value}"
    await show_clients_page(callback.message, page=1, search_name="", filter_by=filter_by)


def register_filter_clients(dp: Dispatcher):
    dp.register_callback_query_handler(start_filter_client, text="client_filter")
    dp.register_callback_query_handler(select_filter_type, lambda c: c.data.startswith("filter_select|"))
    dp.register_callback_query_handler(apply_filter_value, lambda c: c.data.startswith("filter_apply|"))
