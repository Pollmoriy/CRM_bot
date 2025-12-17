# handlers/reports/admin_generate_report.py

import os
from datetime import date, timedelta
from aiogram import types, Dispatcher
from docx import Document
from docx.shared import Inches
from docx2pdf import convert

# Импорт генераторов диаграмм
from handlers.reports.generators import (
    admin_performance,
    admin_deals,
    admin_sales,
    admin_funnel,
    admin_timeline
)


async def generate_report_cb_handler(query: types.CallbackQuery):
    """Выбор периода отчета через Inline-кнопки"""
    await query.answer("⏳ Подготавливаю отчет...")

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("За неделю", callback_data="report_period_week"),
        InlineKeyboardButton("За месяц", callback_data="report_period_month"),
        InlineKeyboardButton("За год", callback_data="report_period_year")
    )
    await query.message.answer("Выберите период отчета:", reply_markup=kb)


async def report_period_cb_handler(query: types.CallbackQuery):
    """Генерация отчета за выбранный период"""
    period_map = {
        "report_period_week": 7,
        "report_period_month": 30,
        "report_period_year": 365
    }
    period_days = period_map.get(query.data, 30)
    await query.answer(f"Генерируем отчет за последние {period_days} дней...")

    # --- Даты периода ---
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    period_label = f"{period_days}d"

    # --- Пути ---
    template_path = "reports/admin_report_template.docx"
    output_dir = "reports/generated"
    os.makedirs(output_dir, exist_ok=True)
    output_word = f"{output_dir}/admin_report_{period_label}.docx"
    output_pdf = f"{output_dir}/admin_report_{period_label}.pdf"

    # --- Генерация диаграмм за выбранный период ---
    performance_img = await admin_performance.generate_admin_performance_diagram(
        start_date=start_date, end_date=end_date, period_label=period_label
    )
    deals_img = await admin_deals.generate_admin_deals_diagram(
        start_date=start_date, end_date=end_date, period_label=period_label
    )
    sales_img = await admin_sales.generate_admin_sales_diagram(
        start_date=start_date, end_date=end_date, period_label=period_label
    )
    funnel_img = await admin_funnel.generate_admin_sales_funnel(
        start_date=start_date, end_date=end_date, period_label=period_label
    )
    timeline_img = await admin_timeline.generate_admin_tasks_timeline_diagram(
        start_date=start_date, end_date=end_date, period_label=period_label
    )

    # --- Словарь для вставки диаграмм в Word ---
    diagrams = {
        "{{diagram_admin_performance}}": performance_img,
        "{{diagram_admin_deals}}": deals_img,
        "{{diagram_admin_sales}}": sales_img,
        "{{diagram_admin_funnel}}": funnel_img,
        "{{diagram_admin_timeline}}": timeline_img,
    }

    # --- Создание Word документа ---
    doc = Document(template_path)
    for paragraph in doc.paragraphs:
        for placeholder, image_path in diagrams.items():
            if placeholder in paragraph.text:
                paragraph.text = ""
                run = paragraph.add_run()
                if os.path.exists(image_path):
                    run.add_picture(image_path, width=Inches(6))
                else:
                    run.add_text(f"[Диаграмма {placeholder} недоступна]")

    # --- Сохраняем Word ---
    doc.save(output_word)

    # --- Конвертируем в PDF ---
    convert(output_word, output_pdf)

    # --- Отправка пользователю ---
    await query.message.answer_document(
        types.InputFile(output_pdf),
        caption=f"📄 Отчет за последние {period_days} дней готов!"
    )
    print(f"✅ Отчет за {period_days} дней сформирован и отправлен.")


def register_admin_generate_report(dp: Dispatcher):
    dp.register_callback_query_handler(generate_report_cb_handler, lambda c: c.data == "report")
    dp.register_callback_query_handler(report_period_cb_handler, lambda c: c.data.startswith("report_period_"))
    print("✅ Хендлеры генерации отчетов зарегистрированы")
