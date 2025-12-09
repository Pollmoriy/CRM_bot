import asyncio

from utils.notifications.reminders import (
    check_task_reminders,
    check_closed_deals
)

async def main():
    print("\n================= ТЕСТ: Напоминания о задачах =================")
    await check_task_reminders()

    print("\n================= ТЕСТ: Закрытые сделки =================")
    await check_closed_deals()

    print("\n================= ТЕСТ ОКОНЧЕН =================\n")

if __name__ == "__main__":
    asyncio.run(main())
