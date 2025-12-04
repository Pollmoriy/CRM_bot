# handlers/deals/tasks.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, safe_answer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from database.db import async_session_maker
from database.models import Deal, User, Task, TaskStatus, TaskPriority, UserRole
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from keyboards.task_filters_kb import task_filters_kb

TASKS_PER_PAGE = 6

# ------------------------------
# Русские подписи для кнопок (отображение)
# ------------------------------
TASK_STATUS_LABELS = {
    "new": "Новая",
    "in_progress": "В работе",
    "done": "Выполнена",
    "overdue": "Просрочена"
}

TASK_PRIORITY_LABELS = {
    "low": "Низкий",
    "medium": "Средний",
    "high": "Высокий"
}


# ------------------------------
# FSM состояния
# ------------------------------
class TaskForm(StatesGroup):
    name = State()
    description = State()
    priority = State()
    deadline = State()
    employee = State()


class TaskEditForm(StatesGroup):
    edit_task_id = State()
    edit_field = State()  # поле, которое редактируем: name/description/deadline/status/priority/employee
    temp_value = State()


# ------------------------------
# Вспомогательные: получить user по telegram id
# ------------------------------
async def get_user_by_telegram(telegram_id: str):
    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return q.scalar_one_or_none()


# ------------------------------
# Загрузка задач с фильтрами (возвращаем список Task)
# ------------------------------
async def load_tasks(deal_id: int, user: User, status_filter: str = "all", priority_filter: str = "all"):
    async with async_session_maker() as session:
        q = select(Task).options(selectinload(Task.employee)).where(Task.id_deal == deal_id)

        # если employee — только свои задачи
        if getattr(user, "role", None) and getattr(user.role, "value", None) == "employee":
            q = q.where(Task.id_employee == user.id_user)

        # статус фильтр (ожидаем имя enum, например 'new', 'in_progress')
        if status_filter != "all":
            try:
                q = q.where(Task.status == TaskStatus[status_filter])
            except Exception:
                pass

        # приоритет фильтр
        if priority_filter != "all":
            try:
                q = q.where(Task.priority == TaskPriority[priority_filter])
            except Exception:
                pass

        res = await session.execute(q)
        return res.scalars().all()


# ------------------------------
# Клавиатура списка задач
# ------------------------------
def build_tasks_keyboard(tasks, page: int, deal_id: int, user: User):
    kb = InlineKeyboardMarkup(row_width=1)
    start = (page - 1) * TASKS_PER_PAGE
    end = start + TASKS_PER_PAGE

    for t in tasks[start:end]:
        status_key = t.status.value if t.status else "new"
        pr_key = t.priority.value if t.priority else "medium"
        emoji = {
            "new": "🆕",
            "in_progress": "⏳",
            "done": "✅",
            "overdue": "⚠️"
        }.get(status_key, "")
        label = f"{emoji} {t.task_name} — {TASK_STATUS_LABELS.get(status_key, status_key)} / {TASK_PRIORITY_LABELS.get(pr_key, pr_key)}"
        kb.add(InlineKeyboardButton(text=label, callback_data=f"task_detail:{t.id_task}"))

    # пагинация
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"tasks_page:{deal_id}:{page-1}"))
    if end < len(tasks):
        nav.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"tasks_page:{deal_id}:{page+1}"))
    if nav:
        kb.row(*nav)

    # компактный фильтр: кнопка "Фильтры" открывает меню фильтров
    kb.add(InlineKeyboardButton("🔎 Фильтры", callback_data=f"tasks_filters:{deal_id}"))

    # для admin/manager — кнопка добавить
    if getattr(user, "role", None) and getattr(user.role, "value", None) in ["admin", "manager"]:
        kb.add(InlineKeyboardButton("➕ Добавить задачу", callback_data=f"task_add:{deal_id}"))

    # назад в карточку сделки добавляем при отправке show_tasks
    return kb


# ------------------------------
# Показ списка задач (callback_or_message может быть CallbackQuery или Message)
# ------------------------------
async def show_tasks(callback_or_message, deal_id: int, user: User, page: int = 1,
                     status_filter: str = "all", priority_filter: str = "all"):
    is_callback = isinstance(callback_or_message, types.CallbackQuery)
    message = callback_or_message.message if is_callback else callback_or_message

    tasks = await load_tasks(deal_id, user, status_filter, priority_filter)

    # Текст заголовка — сохраняем deal_id в тексте, чтобы фильтры могли его взять
    header = f"📋 Задачи сделки ID {deal_id} (страница {page}):\n\n"
    if not tasks:
        body = "Задач не найдено."
    else:
        body_lines = []
        for t in tasks[(page - 1) * TASKS_PER_PAGE: page * TASKS_PER_PAGE]:
            status_key = t.status.value if t.status else "new"
            pr_key = t.priority.value if t.priority else "medium"
            emp = t.employee.full_name if getattr(t, "employee", None) else "—"
            dl = t.deadline.strftime("%Y-%m-%d") if getattr(t, "deadline", None) else "—"
            body_lines.append(
                f"📝 <b>{t.task_name}</b> (ID {t.id_task})\n"
                f"Статус: {TASK_STATUS_LABELS.get(status_key, status_key)} | Приоритет: {TASK_PRIORITY_LABELS.get(pr_key, pr_key)}\n"
                f"Исполнитель: {emp} | Дедлайн: {dl}\n"
            )
        body = "\n".join(body_lines)

    text = header + body

    kb = build_tasks_keyboard(tasks, page, deal_id, user)
    # кнопка назад к сделке
    kb.add(InlineKeyboardButton("◀️ Назад к сделке", callback_data=f"deal_detail:{deal_id}"))

    try:
        if is_callback:
            await safe_answer(callback_or_message)
            await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        # fallback
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ------------------------------
# Обработчики пагинации
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("tasks_page:"))
async def tasks_page_handler(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, deal_id_s, page_s = query.data.split(":", 2)
        deal_id = int(deal_id_s); page = int(page_s)
    except Exception:
        await query.answer("Ошибка навигации")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user:
        await query.answer("Пользователь не найден")
        return

    await show_tasks(query, deal_id, user, page)


# ------------------------------
# Фильтры — компактное меню
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("tasks_filters:"))
async def tasks_filters_menu(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, deal_id_s = query.data.split(":", 1)
        deal_id = int(deal_id_s)
    except Exception:
        await query.answer("Ошибка")
        return

    kb = InlineKeyboardMarkup(row_width=2)
    # Статусы (русские кнопки, callback передаёт 'status:new' и т.д.)
    kb.add(
        InlineKeyboardButton("Все статусы", callback_data=f"tasks_filter_apply:{deal_id}:status:all"),
        InlineKeyboardButton("Новые", callback_data=f"tasks_filter_apply:{deal_id}:status:new"),
        InlineKeyboardButton("В работе", callback_data=f"tasks_filter_apply:{deal_id}:status:in_progress"),
        InlineKeyboardButton("Выполненные", callback_data=f"tasks_filter_apply:{deal_id}:status:done"),
        InlineKeyboardButton("Просроченные", callback_data=f"tasks_filter_apply:{deal_id}:status:overdue")
    )
    # Приоритеты
    kb.add(
        InlineKeyboardButton("Все приоритеты", callback_data=f"tasks_filter_apply:{deal_id}:priority:all"),
        InlineKeyboardButton("Высокий", callback_data=f"tasks_filter_apply:{deal_id}:priority:high"),
        InlineKeyboardButton("Средний", callback_data=f"tasks_filter_apply:{deal_id}:priority:medium"),
        InlineKeyboardButton("Низкий", callback_data=f"tasks_filter_apply:{deal_id}:priority:low")
    )
    kb.add(InlineKeyboardButton("⏪ Назад", callback_data=f"tasks_page:{deal_id}:1"))
    await query.message.edit_text("Выберите фильтр:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("tasks_filter_apply:"))
async def tasks_filter_apply(query: types.CallbackQuery):
    await safe_answer(query)
    # формат: tasks_filter_apply:{deal_id}:{type}:{value}
    try:
        _, deal_id_s, ftype, fval = query.data.split(":", 3)
        deal_id = int(deal_id_s)
    except Exception:
        await query.answer("Ошибка фильтра")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user:
        await query.answer("Пользователь не найден")
        return

    status_filter = "all"
    priority_filter = "all"
    if ftype == "status":
        status_filter = fval
    elif ftype == "priority":
        priority_filter = fval

    # показываем отфильтрованный список (страница 1)
    await show_tasks(query, deal_id, user, page=1, status_filter=status_filter, priority_filter=priority_filter)


# ------------------------------
# Начало создания задачи (FSM) — admin/manager only
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_add:"))
async def task_add_start(query: types.CallbackQuery, state: FSMContext):
    await safe_answer(query)
    try:
        _, deal_id_s = query.data.split(":", 1)
        deal_id = int(deal_id_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user or getattr(user.role, "value", None) not in ["admin", "manager"]:
        await query.answer("❌ У вас нет прав для создания задачи")
        return

    await state.update_data(deal_id=deal_id, creator_id=user.id_user)
    await query.message.answer("Введите название задачи:")
    await TaskForm.name.set()


@dp.message_handler(state=TaskForm.name)
async def task_form_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите описание (или отправьте пустое сообщение):")
    await TaskForm.description.set()


@dp.message_handler(state=TaskForm.description)
async def task_form_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    # выбор приоритета (русские подписи)
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("Низкий", callback_data="task_prio:low"),
        InlineKeyboardButton("Средний", callback_data="task_prio:medium"),
        InlineKeyboardButton("Высокий", callback_data="task_prio:high")
    )
    await message.answer("Выберите приоритет:", reply_markup=kb)
    await TaskForm.priority.set()


@dp.callback_query_handler(lambda c: c.data.startswith("task_prio:"), state=TaskForm.priority)
async def task_form_priority(query: types.CallbackQuery, state: FSMContext):
    await safe_answer(query)
    try:
        _, pr = query.data.split(":", 1)
    except Exception:
        await query.answer("Ошибка")
        return
    if pr not in TaskPriority.__members__:
        pr = "medium"
    await state.update_data(priority=pr)
    await query.message.answer("Введите дедлайн в формате ГГГГ-ММ-ДД или отправьте пустое сообщение:")
    await TaskForm.deadline.set()


@dp.message_handler(state=TaskForm.deadline)
async def task_form_deadline(message: types.Message, state: FSMContext):
    txt = message.text.strip()
    dl = None
    if txt:
        try:
            dl = datetime.strptime(txt, "%Y-%m-%d").date()
        except Exception:
            await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
            return
    await state.update_data(deadline=dl)

    # список сотрудников (role == employee)
    async with async_session_maker() as session:
        res = await session.execute(select(User).where(User.role == UserRole.employee))
        employees = res.scalars().all()

    if not employees:
        await message.answer("В системе нет сотрудников для назначения.")
        await state.finish()
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for e in employees:
        kb.add(InlineKeyboardButton(e.full_name, callback_data=f"task_assign:{e.id_user}"))
    await message.answer("Выберите исполнителя:", reply_markup=kb)
    await TaskForm.employee.set()


@dp.callback_query_handler(lambda c: c.data.startswith("task_assign:"), state=TaskForm.employee)
async def task_form_assign(query: types.CallbackQuery, state: FSMContext):
    await safe_answer(query)
    try:
        _, emp_s = query.data.split(":", 1)
        emp_id = int(emp_s)
    except Exception:
        await query.answer("Ошибка")
        return

    data = await state.get_data()
    deal_id = data.get("deal_id")
    name = data.get("name")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    deadline = data.get("deadline", None)

    async with async_session_maker() as session:
        new_task = Task(
            task_name=name,
            description=description,
            id_employee=emp_id,
            id_deal=deal_id,
            status=TaskStatus.new,
            priority=TaskPriority[priority] if priority in TaskPriority.__members__ else TaskPriority.medium,
            deadline=deadline
        )
        session.add(new_task)
        await session.commit()

    await query.message.answer("✅ Задача создана.")
    await state.finish()

    user = await get_user_by_telegram(str(query.from_user.id))
    if user:
        await show_tasks(query, deal_id, user, page=1)


# ------------------------------
# Просмотр деталей задачи и меню редактирования
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_detail:"))
async def task_detail(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, task_s = query.data.split(":", 1)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id, options=[selectinload(Task.employee), selectinload(Task.deal)])
        user = await get_user_by_telegram(str(query.from_user.id))

    if not task:
        await query.answer("Задача не найдена")
        return

    status_label = TASK_STATUS_LABELS.get(task.status.value if task.status else "new", task.status.value if task.status else "new")
    pr_label = TASK_PRIORITY_LABELS.get(task.priority.value if task.priority else "medium", task.priority.value if task.priority else "medium")
    emp = task.employee.full_name if getattr(task, "employee", None) else "—"
    dl = task.deadline.strftime("%Y-%m-%d") if getattr(task, "deadline", None) else "—"

    text = (
        f"📝 <b>{task.task_name}</b>\n"
        f"{task.description or '—'}\n\n"
        f"Статус: {status_label}\n"
        f"Приоритет: {pr_label}\n"
        f"Исполнитель: {emp}\n"
        f"Дедлайн: {dl}\n"
        f"Сделка ID: {task.id_deal}\n"
    )

    kb = InlineKeyboardMarkup(row_width=2)

    # Employee может менять только статус своей задачи
    if user and getattr(user.role, "value", None) == "employee" and task.id_employee == user.id_user:
        # показываем кнопку для перехода по статусу (new -> in_progress -> done)
        next_status = None
        if task.status and task.status == TaskStatus.new:
            next_status = "in_progress"
            kb.add(InlineKeyboardButton("В работу", callback_data=f"task_status_change:{task.id_task}:in_progress"))
        elif task.status and task.status == TaskStatus.in_progress:
            next_status = "done"
            kb.add(InlineKeyboardButton("Отметить выполненной", callback_data=f"task_status_change:{task.id_task}:done"))
        # также можно вернуть в работу, если нужно (опционально)
    else:
        # admin/manager: меню редактирования
        if user and getattr(user.role, "value", None) in ["admin", "manager"]:
            kb.add(InlineKeyboardButton("Изменить", callback_data=f"task_edit_menu:{task.id_task}"))
            kb.add(InlineKeyboardButton("Удалить", callback_data=f"task_delete_confirm:{task.id_task}"))

    kb.add(InlineKeyboardButton("◀️ Назад к списку задач", callback_data=f"deal_tasks:{task.id_deal}"))

    await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ------------------------------
# Быстрая смена статуса сотрудником или менеджером
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_status_change:"))
async def task_status_change(query: types.CallbackQuery):
    await safe_answer(query)
    # формат: task_status_change:{task_id}:{new_status}
    try:
        _, task_s, new_status = query.data.split(":", 2)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user:
        await query.answer("Пользователь не найден")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id)
        if not task:
            await query.answer("Задача не найдена")
            return

        # если employee — проверить что задача их
        if getattr(user.role, "value", None) == "employee" and task.id_employee != user.id_user:
            await query.answer("❌ Это не ваша задача")
            return

        # применяем статус
        try:
            task.status = TaskStatus[new_status]
        except Exception:
            await query.answer("Неверный статус")
            return

        if new_status == "done":
            task.date_completed = date.today()
        await session.commit()
        deal_id = task.id_deal

    await query.answer("Статус обновлён")
    await show_tasks(query, deal_id, user, page=1)


# ------------------------------
# Удаление — подтверждение -> удаление
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_delete_confirm:"))
async def task_delete_confirm(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, task_s = query.data.split(":", 1)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id, options=[selectinload(Task.deal)])
        if not task:
            await query.answer("Задача не найдена")
            return

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Удалить", callback_data=f"task_delete:{task_id}"),
        InlineKeyboardButton("Отмена", callback_data=f"task_detail:{task_id}")
    )
    await query.message.edit_text(f"Вы действительно хотите удалить задачу '{task.task_name}'?", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("task_delete:"))
async def task_delete(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, task_s = query.data.split(":", 1)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user or getattr(user.role, "value", None) not in ["admin", "manager"]:
        await query.answer("❌ У вас нет прав на удаление")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id, options=[selectinload(Task.deal)])
        if not task:
            await query.answer("Задача не найдена")
            return
        deal_id = task.id_deal
        await session.delete(task)
        await session.commit()

    await query.answer("Задача удалена")
    await show_tasks(query, deal_id, user, page=1)


# ------------------------------
# Редактирование — меню выбора поля (admin/manager)
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_edit_menu:"))
async def task_edit_menu(query: types.CallbackQuery, state: FSMContext):
    await safe_answer(query)
    try:
        _, task_s = query.data.split(":", 1)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user or getattr(user.role, "value", None) not in ["admin", "manager"]:
        await query.answer("❌ У вас нет прав")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id)
        if not task:
            await query.answer("Задача не найдена")
            return

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Изменить название", callback_data=f"task_edit_field:{task_id}:name"),
        InlineKeyboardButton("Изменить описание", callback_data=f"task_edit_field:{task_id}:description")
    )
    kb.add(
        InlineKeyboardButton("Изменить срок", callback_data=f"task_edit_field:{task_id}:deadline"),
        InlineKeyboardButton("Изменить статус", callback_data=f"task_edit_field:{task_id}:status")
    )
    kb.add(
        InlineKeyboardButton("Изменить приоритет", callback_data=f"task_edit_field:{task_id}:priority")
    )
    kb.add(InlineKeyboardButton("Отмена", callback_data=f"task_detail:{task_id}"))
    await query.message.edit_text("Выберите, что изменить:", reply_markup=kb)


# ------------------------------
# Обработчик выбора поля для редактирования
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_edit_field:"))
async def task_edit_field(query: types.CallbackQuery, state: FSMContext):
    await safe_answer(query)
    try:
        _, task_s, field = query.data.split(":", 2)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user or getattr(user.role, "value", None) not in ["admin", "manager"]:
        await query.answer("❌ У вас нет прав")
        return

    await state.update_data(edit_task_id=task_id, edit_field=field)

    # В зависимости от поля — запрашиваем ввод или показываем подменю
    if field in ["name", "description"]:
        prompt = "Введите новое значение:" if field == "name" else "Введите новое описание:"
        await query.message.edit_text(prompt)
        await TaskEditForm.temp_value.set()
    elif field == "deadline":
        await query.message.edit_text("Введите новый дедлайн в формате ГГГГ-ММ-ДД или отправьте пустое сообщение для удаления:")
        await TaskEditForm.temp_value.set()
    elif field == "status":
        kb = InlineKeyboardMarkup(row_width=2)
        for s in TaskStatus:
            kb.insert(InlineKeyboardButton(TASK_STATUS_LABELS.get(s.value, s.value), callback_data=f"task_do_edit:{task_id}:status:{s.name}"))
        kb.add(InlineKeyboardButton("Отмена", callback_data=f"task_detail:{task_id}"))
        await query.message.edit_text("Выберите статус:", reply_markup=kb)
    elif field == "priority":
        kb = InlineKeyboardMarkup(row_width=2)
        for p in TaskPriority:
            kb.insert(InlineKeyboardButton(TASK_PRIORITY_LABELS.get(p.value, p.value), callback_data=f"task_do_edit:{task_id}:priority:{p.name}"))
        kb.add(InlineKeyboardButton("Отмена", callback_data=f"task_detail:{task_id}"))
        await query.message.edit_text("Выберите приоритет:", reply_markup=kb)
    else:
        await query.answer("Неизвестное поле")
        await state.finish()


# ------------------------------
# Применение текстового ввода для редактирования (name/description/deadline)
# ------------------------------
@dp.message_handler(state=TaskEditForm.temp_value)
async def task_edit_apply_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("edit_task_id")
    field = data.get("edit_field")
    if not task_id or not field:
        await message.answer("Внутренняя ошибка.")
        await state.finish()
        return

    val = message.text.strip()
    new_value = None
    if field == "deadline":
        if val == "":
            new_value = None
        else:
            try:
                new_value = datetime.strptime(val, "%Y-%m-%d").date()
            except Exception:
                await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
                return
    else:
        new_value = val

    async with async_session_maker() as session:
        task = await session.get(Task, task_id)
        if not task:
            await message.answer("Задача не найдена.")
            await state.finish()
            return

        if field == "name":
            task.task_name = new_value
        elif field == "description":
            task.description = new_value
        elif field == "deadline":
            task.deadline = new_value

        await session.commit()
        deal_id = task.id_deal

    await message.answer("Изменения сохранены.")
    await state.finish()
    user = await get_user_by_telegram(str(message.from_user.id))
    if user:
        await show_tasks(message, deal_id, user, page=1)


# ------------------------------
# Применение редактирования через кнопки (status/priority/employee)
# формат callback: task_do_edit:{task_id}:{field}:{value_name}
# ------------------------------
@dp.callback_query_handler(lambda c: c.data.startswith("task_do_edit:"))
async def task_do_edit(query: types.CallbackQuery):
    await safe_answer(query)
    try:
        _, task_s, field, val = query.data.split(":", 3)
        task_id = int(task_s)
    except Exception:
        await query.answer("Ошибка")
        return

    user = await get_user_by_telegram(str(query.from_user.id))
    if not user or getattr(user.role, "value", None) not in ["admin", "manager"]:
        await query.answer("❌ У вас нет прав")
        return

    async with async_session_maker() as session:
        task = await session.get(Task, task_id)
        if not task:
            await query.answer("Задача не найдена")
            return

        if field == "status":
            try:
                task.status = TaskStatus[val]
            except Exception:
                await query.answer("Неверный статус")
                return
            if val == "done":
                task.date_completed = date.today()
        elif field == "priority":
            try:
                task.priority = TaskPriority[val]
            except Exception:
                await query.answer("Неверный приоритет")
                return
        elif field == "employee":
            try:
                new_emp = int(val)
                task.id_employee = new_emp
            except Exception:
                await query.answer("Неверный сотрудник")
                return

        await session.commit()
        deal_id = task.id_deal

    await query.answer("Поле обновлено")
    await show_tasks(query, deal_id, user, page=1)


# ------------------------------
# Хелперы
# ------------------------------
async def await_user_from_callback(callback: types.CallbackQuery):
    return await get_user_by_telegram(str(callback.from_user.id))

async def await_user_from_message(message: types.Message):
    return await get_user_by_telegram(str(message.from_user.id))
