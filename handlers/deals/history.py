# handlers/deals/history.py

from aiogram import types
from loader import dp, safe_answer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.db import async_session_maker
from database.models import AuditLog, User


# ============================
#  ПОКАЗ ИСТОРИИ ИЗМЕНЕНИЙ
# ============================

@dp.callback_query_handler(lambda c: c.data.startswith("deal_history_"))
async def show_deal_history(callback: types.CallbackQuery):
    await safe_answer(callback)

    deal_id = int(callback.data.split("_")[-1])
    telegram_id = str(callback.from_user.id)

    # загружаем пользователя
    async with async_session_maker() as session:
        user_q = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_q.scalar_one_or_none()

        if not user:
            await callback.message.answer("⚠️ Пользователь не найден.")
            return

        # грузим логи (только по этой сделке)
        logs_q = await session.execute(
            select(AuditLog)
            .where(AuditLog.table_name == "deals")
            .where(AuditLog.record_id == deal_id)
            .order_by(AuditLog.action_time.desc())
            .options(selectinload(AuditLog.user))
        )

        logs = logs_q.scalars().all()

    # если логов нет
    if not logs:
        try:
            await callback.message.edit_text(
                "📜 История изменений пуста."
            )
        except:
            await callback.message.answer(
                "📜 История изменений пуста."
            )
        return

    # формирование текста
    text_lines = ["<b>📜 История изменений сделки:</b>\n"]

    for log in logs:
        user_name = log.user.full_name if log.user else "Неизвестный пользователь"
        text_lines.append(
            f"• <b>{log.action}</b> — <i>{log.action_time.strftime('%Y-%m-%d %H:%M')}</i>\n"
            f"   Пользователь: {user_name}\n"
            f"   Детали: {log.details or '—'}\n"
        )

    text = "\n".join(text_lines)

    # кнопка Назад
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("◀️ Назад", callback_data=f"deal_detail_{deal_id}"))

    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except:
        await callback.message.answer(text, reply_markup=kb)
