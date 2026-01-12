import os
from typing import List
from telebot import TeleBot

MAX_PREVIEW = 20
REPORTS_DIR = "reports_output"

os.makedirs(REPORTS_DIR, exist_ok=True)


def send_report_with_preview(
    *,
    bot: TeleBot,
    chat_id: int,
    title: str,
    items: List[str],
    empty_message: str = "✅ Нарушений не найдено",
    filename_prefix: str = "report"
) -> None:
    """
    Универсальная отправка отчёта:
    - превью в чат (первые MAX_PREVIEW строк)
    - полный список в файле, если строк больше MAX_PREVIEW
    """

    if not items:
        bot.send_message(chat_id, empty_message)
        return

    preview = items[:MAX_PREVIEW]

    message = f"{title}\n\n"
    message += f"<i>Найдено записей: {len(items)}\n\n</i>"

    for item in preview:
        message += f"• {item}\n"

    if len(items) > MAX_PREVIEW:
        message += "\n📎 <b>Полный список прикреплён файлом</b> 👇"

    bot.send_message(chat_id, message, parse_mode='HTML')

    # Отправка файла при необходимости
    if len(items) > MAX_PREVIEW:
        file_path = os.path.join(
            REPORTS_DIR,
            f"{filename_prefix}_{chat_id}.txt"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(item + "\n")

        with open(file_path, "rb") as f:
            bot.send_document(chat_id, f)
