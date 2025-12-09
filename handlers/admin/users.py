# handlers/users.py
import enum
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from loader import dp, safe_answer
from sqlalchemy import select, and_
from database.db import async_session_maker
from database.models import User, UserRole, AuditLog

USERS_PER_PAGE = 6
MANAGERS_PER_PAGE = 5


# =============================
# FSM для поиска пользователей
# =============================
class SearchUserStates(StatesGroup):
    waiting_for_name = State()


# =============================
# Загрузка пользователей с фильтром и поиском
# =============================
async def load_users(search_name: str = "", role_filter: str = "all"):
    conditions = []
    if search_name:
        conditions.append(User.full_name.ilike(f"%{search_name}%"))
    if role_filter and role_filter != "all":
        try:
            conditions.append(User.role == UserRole[role_filter])
        except Exception:
            pass
    async with async_session_maker() as session:
        q = select(User).order_by(User.full_name)
        if conditions:
            q = q.where(and_(*conditions))
        res = await session.execute(q)
        return res.scalars().all()


# =============================
# Верхнее меню: поиск + фильтр + обновить
# =============================
def users_top_menu(page=1, search_name="", role_filter="all"):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🔎 Поиск", callback_data=f"user_search_start|{page}|{search_name}|{role_filter}"),
        InlineKeyboardButton("🎚️ Фильтр", callback_data=f"user_filter_start|{page}|{search_name}|{role_filter}"),
    )
    return kb


# =============================
# Клавиатура списка пользователей с пагинацией
# =============================
def get_users_keyboard(users, page: int, search_name: str, role_filter: str):
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    for u in users[start:end]:
        status = "🔓" if u.is_active else "🔒"
        kb.add(
            InlineKeyboardButton(
                text=f"{u.full_name} — {u.role.value} {status}",
                callback_data=f"user_open|{u.id_user}|{search_name or ''}|{role_filter}|{page}"
            )
        )

    nav_row = []
    if start > 0:
        nav_row.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"user_page|{page-1}|{search_name or ''}|{role_filter}")
        )
    if end < len(users):
        nav_row.append(
            InlineKeyboardButton("➡️ Вперед", callback_data=f"user_page|{page+1}|{search_name or ''}|{role_filter}")
        )
    if nav_row:
        kb.row(*nav_row)
    return kb


# =============================
# Показ списка пользователей
# =============================
async def show_users_list(message_or_callback, page: int = 1, search_name: str = "", role_filter: str = "all"):
    is_callback = isinstance(message_or_callback, types.CallbackQuery)
    message = message_or_callback.message if is_callback else message_or_callback

    users = await load_users(search_name, role_filter)

    if not users:
        kb = users_top_menu(page, search_name, role_filter)
        text = "Пользователей не найдено."
        try:
            if is_callback:
                await safe_answer(message_or_callback)
                await message.edit_text(text, reply_markup=kb)
            else:
                await message.answer(text, reply_markup=kb)
        except:
            await message.answer(text)
        return

    kb = users_top_menu(page, search_name, role_filter)
    list_kb = get_users_keyboard(users, page, search_name, role_filter)

    # добавляем все ряды списка под верхним меню
    for row in list_kb.inline_keyboard:
        kb.row(*row)

    text = f"📋 Список пользователей (страница {page})"
    if search_name or role_filter != "all":
        text += f"\nФильтр: {role_filter} | Поиск: «{search_name}»"

    try:
        if is_callback:
            await safe_answer(message_or_callback)
            await message.edit_text(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)
    except:
        await message.answer(text, reply_markup=kb)


# =============================
# Обработчик кнопки "⚙️ Пользователи"
# =============================
@dp.message_handler(lambda message: message.text == "⚙️ Пользователи")
async def handle_admin_users(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with async_session_maker() as session:
        user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        current = user_q.scalar_one_or_none()
    if not current or getattr(current.role, "value", None) != UserRole.admin.value:
        await message.answer("⚠️ Доступ запрещён. Только для админов.")
        return
    await show_users_list(message, page=1, search_name="", role_filter="all")


# =============================
# Поиск пользователей (FSM)
# =============================
@dp.callback_query_handler(lambda c: c.data.startswith("user_search_start|"))
async def user_search_start(callback: types.CallbackQuery):
    await safe_answer(callback)
    await callback.message.answer("Введите часть имени для поиска:", reply_markup=None)
    await SearchUserStates.waiting_for_name.set()
    state = dp.current_state(chat=callback.from_user.id, user=callback.from_user.id)
    try:
        _, page_s, search_name, role_filter = callback.data.split("|", 3)
        await state.update_data(page=int(page_s), role_filter=role_filter)
    except:
        await state.update_data(page=1, role_filter="all")


@dp.message_handler(state=SearchUserStates.waiting_for_name)
async def process_user_search(message: types.Message, state: FSMContext):
    search_text = message.text.strip()
    data = await state.get_data()
    page = int(data.get("page", 1))
    role_filter = data.get("role_filter", "all")
    await state.finish()
    await show_users_list(message, page=1, search_name=search_text, role_filter=role_filter)


# =============================
# Фильтр по ролям
# =============================
def user_filter_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Админы", callback_data="user_filter|admin"),
        InlineKeyboardButton("Менеджеры", callback_data="user_filter|manager"),
        InlineKeyboardButton("Сотрудники", callback_data="user_filter|employee"),
        InlineKeyboardButton("❌ Без фильтра", callback_data="user_filter|all"),
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="user_page|1||all"))
    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("user_filter_start|"))
async def start_filter_users(callback: types.CallbackQuery):
    await safe_answer(callback)
    await callback.message.edit_text("Выберите роль:", reply_markup=user_filter_menu())


@dp.callback_query_handler(lambda c: c.data.startswith("user_filter|"))
async def apply_user_role_filter(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, role = callback.data.split("|")
    await show_users_list(callback, page=1, search_name="", role_filter=role)


# =============================
# Пагинация списка пользователей
# =============================
@dp.callback_query_handler(lambda c: c.data.startswith("user_page|"))
async def paginate_users(callback: types.CallbackQuery):
    await safe_answer(callback)
    try:
        _, page, search_name, role_filter = callback.data.split("|")
        page = int(page)
    except:
        await callback.answer("Ошибка навигации.")
        return
    await show_users_list(callback, page=page, search_name=search_name, role_filter=role_filter)


# =============================
# Детали пользователя и действия
# =============================
def user_actions_kb(user: User):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("✏ Изменить роль", callback_data=f"user_change_role|{user.id_user}"),
        InlineKeyboardButton(
            "🔓 Разблокировать" if not user.is_active else "🔒 Заблокировать",
            callback_data=f"user_toggle_block|{user.id_user}",
        ),
    )
    kb.add(InlineKeyboardButton("👨‍💼 Назначить менеджера", callback_data=f"user_assign_manager|{user.id_user}"))
    kb.add(InlineKeyboardButton("📜 История", callback_data=f"user_history|{user.id_user}"))
    kb.add(InlineKeyboardButton("🔙 Назад к списку", callback_data="user_page|1||all"))
    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("user_open|"))
async def open_user(callback: types.CallbackQuery):
    await safe_answer(callback)
    try:
        _, user_id, search_name, role_filter, page = callback.data.split("|")
        user_id = int(user_id)
        page = int(page)
        async with async_session_maker() as session:
            user = await session.get(User, user_id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        await callback.message.edit_text(
            f"👤 <b>{user.full_name}</b>\n"
            f"ID: {user.id_user}\n"
            f"Роль: {user.role}\n"
            f"Статус: {'Активен' if user.is_active else 'Заблокирован'}",
            reply_markup=user_actions_kb(user)
        )
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")


# =============================
# Смена роли пользователя
# =============================
def change_role_kb(user_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("admin", callback_data=f"user_set_role|{user_id}|admin"),
        InlineKeyboardButton("manager", callback_data=f"user_set_role|{user_id}|manager"),
        InlineKeyboardButton("employee", callback_data=f"user_set_role|{user_id}|employee"),
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data=f"user_open|{user_id}| ||all|1"))
    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("user_change_role|"))
async def user_change_role(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id = callback.data.split("|")
    await callback.message.edit_text(
        "Выберите новую роль:",
        reply_markup=change_role_kb(int(user_id))
    )


@dp.callback_query_handler(lambda c: c.data.startswith("user_set_role|"))
async def user_set_role(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id, new_role = callback.data.split("|")
    user_id = int(user_id)
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        user.role = new_role
        await session.commit()
    await callback.message.edit_text(
        f"Роль изменена на <b>{new_role}</b>",
        reply_markup=user_actions_kb(user)
    )


# =============================
# Блокировка / Разблокировка
# =============================
@dp.callback_query_handler(lambda c: c.data.startswith("user_toggle_block|"))
async def toggle_block(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id = callback.data.split("|")
    user_id = int(user_id)
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        user.is_active = not user.is_active
        await session.commit()
        status = "разблокирован" if user.is_active else "заблокирован"
    await callback.message.edit_text(
        f"Пользователь <b>{user.full_name}</b> теперь {status}",
        reply_markup=user_actions_kb(user)
    )


# =============================
# Назначение менеджера
# =============================
async def managers_list_kb(user_id: int, page=1):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User.id_user, User.full_name).where(User.role == "manager")
        )
        managers = result.all()
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * MANAGERS_PER_PAGE
    end = start + MANAGERS_PER_PAGE
    for m_id, name in managers[start:end]:
        kb.add(InlineKeyboardButton(name, callback_data=f"user_set_manager|{user_id}|{m_id}"))
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"user_mgr_page|{user_id}|{page-1}"))
    if end < len(managers):
        nav.append(InlineKeyboardButton("➡️", callback_data=f"user_mgr_page|{user_id}|{page+1}"))
    if nav:
        kb.row(*nav)
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data=f"user_open|{user_id}| ||all|1"))
    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("user_assign_manager|"))
async def assign_manager(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id = callback.data.split("|")
    kb = await managers_list_kb(int(user_id), page=1)
    await callback.message.edit_text("Выберите менеджера:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("user_mgr_page|"))
async def assign_manager_page(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id, page = callback.data.split("|")
    kb = await managers_list_kb(int(user_id), int(page))
    await callback.message.edit_text("Выберите менеджера:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("user_set_manager|"))
async def set_manager(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id, manager_id = callback.data.split("|")
    async with async_session_maker() as session:
        user = await session.get(User, int(user_id))
        user.manager_id = int(manager_id)
        await session.commit()
    await callback.message.edit_text("Менеджер назначен!", reply_markup=user_actions_kb(user))


# =============================
# История действий пользователя
# =============================
@dp.callback_query_handler(lambda c: c.data.startswith("user_history|"))
async def user_history(callback: types.CallbackQuery):
    await safe_answer(callback)
    _, user_id = callback.data.split("|")
    async with async_session_maker() as session:
        result = await session.execute(
            select(AuditLog).where(AuditLog.id_user == int(user_id)).order_by(AuditLog.action_time.desc()).limit(20)
        )
        logs = result.scalars().all()
    text = "<b>История действий:</b>\n\n"
    if not logs:
        text += "Нет записей."
    else:
        for log in logs:
            text += (
                f"📌 <b>{log.action}</b>\n"
                f"Таблица: {log.table_name}\n"
                f"Запись: {log.record_id}\n"
                f"Время: {log.action_time}\n"
                f" ℹ️ {log.details}\n\n"
            )
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data=f"user_open|{user_id}| ||all|1"))
    await callback.message.edit_text(text, reply_markup=kb)


# =============================
# Регистрация коллбеков (для удобства)
# =============================
def register_users_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_admin_users, lambda m: m.text == "⚙️ Пользователи")
