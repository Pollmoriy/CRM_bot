from aiogram import types
from keyboards.admin_kb import admin_menu
from keyboards.manager_kb import manager_menu
from keyboards.employee_kb import employee_menu
from database.models import UserRole

async def show_main_menu(message: types.Message, role: str):
    if role == UserRole.admin.value:
        await message.answer("Вы вошли как Админ", reply_markup=admin_menu)
    elif role == UserRole.manager.value:
        await message.answer("Вы вошли как Менеджер", reply_markup=manager_menu)
    else:
        await message.answer("Вы вошли как Сотрудник", reply_markup=employee_menu)
