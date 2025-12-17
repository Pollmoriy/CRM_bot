import os
from datetime import date, timedelta

from aiogram import types, Dispatcher
from docx import Document
from docx.shared import Inches
from docx2pdf import convert
from sqlalchemy import select

from database.db import async_session_maker
from database.models import User, Deal, Task, TaskStatus

from handlers.reports.generators import (
    admin_performance,
    admin_deals,
    admin_sales,
    admin_funnel,
    admin_timeline
)

# -------------------------------------------------
# 🖼 ЗАМЕНА ДИАГРАММ (ОТДЕЛЬНО!)
# -------------------------------------------------
def replace_diagram_placeholders(doc, diagram_map: dict):
    print("🖼 Начинаю замену диаграмм")

    for p_idx, paragraph in enumerate(doc.paragraphs):
        for placeholder, image_path in diagram_map.items():
            if placeholder in paragraph.text:
                print(f"🖼 Найден плейсхолдер {placeholder} в абзаце {p_idx}")

                paragraph.text = ""
                run = paragraph.add_run()

                if os.path.exists(image_path):
                    run.add_picture(image_path, width=Inches(6))
                    print(f"✅ Диаграмма вставлена: {image_path}")
                else:
                    run.add_text(f"[Диаграмма {placeholder} недоступна]")
                    print(f"⚠️ Файл не найден: {image_path}")


# -------------------------------------------------
# 📝 ЗАМЕНА ТЕКСТА С СОХРАНЕНИЕМ СТИЛЯ
# -------------------------------------------------
def replace_text_placeholders_preserve_style(doc, replacements: dict):
    print("📝 Начинаю замену текстовых плейсхолдеров")

    for p_idx, paragraph in enumerate(doc.paragraphs):
        if not paragraph.runs:
            continue

        original_text = paragraph.text
        new_text = original_text

        for key, value in replacements.items():
            if key in new_text:
                print(f"📝 Абзац {p_idx}: {key} → {value}")
                new_text = new_text.replace(key, str(value))

        if new_text != original_text:
            first_run = paragraph.runs[0]

            style = {
                "bold": first_run.bold,
                "italic": first_run.italic,
                "underline": first_run.underline,
                "font_name": first_run.font.name,
                "font_size": first_run.font.size,
                "font_color": first_run.font.color.rgb,
            }

            for run in paragraph.runs:
                run.text = ""

            run = paragraph.add_run(new_text)

            run.bold = style["bold"]
            run.italic = style["italic"]
            run.underline = style["underline"]

            if style["font_name"]:
                run.font.name = style["font_name"]
            if style["font_size"]:
                run.font.size = style["font_size"]
            if style["font_color"]:
                run.font.color.rgb = style["font_color"]

            print(f"✅ Абзац {p_idx} обновлён со стилем")


# -------------------------------------------------
# 📌 КНОПКА «ОТЧЁТ»
# -------------------------------------------------
async def generate_report_cb_handler(query: types.CallbackQuery):
    await query.answer("📊 Формирование отчёта")

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("За неделю", callback_data="report_period_week"),
        InlineKeyboardButton("За месяц", callback_data="report_period_month"),
        InlineKeyboardButton("За год", callback_data="report_period_year"),
    )

    await query.message.answer("Выберите период отчёта:", reply_markup=kb)


# -------------------------------------------------
# 📊 ГЕНЕРАЦИЯ ОТЧЁТА
# -------------------------------------------------
async def report_period_cb_handler(query: types.CallbackQuery):
    try:
        period_days = {
            "report_period_week": 7,
            "report_period_month": 30,
            "report_period_year": 365,
        }.get(query.data, 30)

        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        print(f"📅 Период отчёта: {start_date} → {end_date}")

        # -------------------------
        # 👤 АДМИН
        # -------------------------
        async with async_session_maker() as session:
            admin = await session.scalar(
                select(User).where(User.telegram_id == query.from_user.id)
            )
            admin_name = admin.full_name if admin else "Администратор"
            print(f"👤 Администратор отчёта: {admin_name}")

            # -------------------------
            # 📊 СДЕЛКИ
            # -------------------------
            deals = (await session.execute(select(Deal))).scalars().all()

            deal_stats = {
                "Новая": 0,
                "В работе": 0,
                "Приостановлена": 0,
                "Закрыта": 0,
            }

            for d in deals:
                if d.stage:
                    deal_stats[d.stage.value] += 1

            total_deals = sum(deal_stats.values())
            conversion_rate = round(
                deal_stats["Закрыта"] / total_deals * 100, 1
            ) if total_deals else 0

            # -------------------------
            # 📊 ЗАДАЧИ
            # -------------------------
            tasks = (await session.execute(select(Task))).scalars().all()

            total_created = len(tasks)
            total_done = sum(1 for t in tasks if t.status == TaskStatus.done)
            total_overdue = sum(1 for t in tasks if t.status == TaskStatus.overdue)

            employees = {t.id_employee for t in tasks if t.id_employee}
            avg_load = round(total_created / max(len(employees), 1), 1)

        # -------------------------
        # 🖼 ДИАГРАММЫ
        # -------------------------
        label = f"{period_days}d"

        await admin_performance.generate_admin_performance_diagram(start_date, end_date, label)
        await admin_deals.generate_admin_deals_diagram(start_date, end_date, label)
        await admin_sales.generate_admin_sales_diagram(start_date, end_date, label)
        await admin_funnel.generate_admin_sales_funnel(start_date, end_date, label)
        await admin_timeline.generate_admin_tasks_timeline_diagram(start_date, end_date, label)

        # -------------------------
        # 📄 WORD → PDF
        # -------------------------
        template = "reports/admin_report_template.docx"
        output_dir = "reports/generated"
        os.makedirs(output_dir, exist_ok=True)

        docx_path = f"{output_dir}/admin_report_{label}.docx"
        pdf_path = f"{output_dir}/admin_report_{label}.pdf"

        doc = Document(template)

        # 🖼 диаграммы
        replace_diagram_placeholders(doc, {
            "{{diagram_admin_performance}}": f"reports/images/admin_performance_report_{label}.png",
            "{{diagram_admin_deals}}": f"reports/images/admin_deals_progress_{label}.png",
            "{{diagram_admin_sales}}": f"reports/images/admin_sales_by_clients_{label}.png",
            "{{diagram_admin_funnel}}": f"reports/images/admin_sales_funnel_{label}.png",
            "{{diagram_admin_timeline}}": f"reports/images/admin_tasks_timeline_{label}.png",
        })

        # 📝 текст
        replace_text_placeholders_preserve_style(doc, {
            "{admin_name}": admin_name,
            "{date_start}": start_date.strftime("%d.%m.%Y"),
            "{date_end}": end_date.strftime("%d.%m.%Y"),

            "{total_deals}": total_deals,
            "{new_deals}": deal_stats["Новая"],
            "{in_progress_deals}": deal_stats["В работе"],
            "{on_hold_deals}": deal_stats["Приостановлена"],
            "{completed_deals}": deal_stats["Закрыта"],
            "{conversion_rate}": conversion_rate,

            "{total_created}": total_created,
            "{total_done}": total_done,
            "{total_overdue}": total_overdue,
            "{avg_load}": avg_load,
        })

        doc.save(docx_path)
        convert(docx_path, pdf_path)

        await query.message.answer_document(
            types.InputFile(pdf_path),
            caption=f"📄 Отчёт за {period_days} дней сформирован"
        )

        print("✅ Отчёт успешно отправлен")

    except Exception as e:
        print("⚠️ Ошибка генерации отчёта:", e)
        await query.message.answer(f"⚠️ Ошибка генерации отчёта: {e}")


def register_admin_generate_report(dp: Dispatcher):
    dp.register_callback_query_handler(generate_report_cb_handler, lambda c: c.data == "report")
    dp.register_callback_query_handler(report_period_cb_handler, lambda c: c.data.startswith("report_period_"))
    print("✅ admin_generate_report зарегистрирован")
