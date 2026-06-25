"""
Python Course Bot — Telegram-бот для изучения Python.

39 уроков в 8 модулях: от арифметики до фриланса.
Хранение: SQLite. Фичи: прогресс, streak, закладки, тесты, сертификат, админка.

Запуск:
    pip install -r requirements.txt
    export TELEGRAM_BOT_TOKEN="токен"
    export ADMIN_IDS="id1,id2"          # опционально
    python bot.py

Деплой на Render.com:
    1. Fork репозитория
    2. Render → New → Web Service
    3. Добавить env: TELEGRAM_BOT_TOKEN, ADMIN_IDS
    4. Deploy
"""
import logging
from datetime import time

from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)

from core.config import BOT_TOKEN, COURSE_DIR
from core.web_server import start_web_server
from core.handlers import (
    start, help_command, reset_command, random_command,
    bookmark_command, stats_command, health,
    settings_command, export_command,
    admin_command, broadcast_command,
    button_handler, search_handler, daily_lesson,
)

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def main():
    start_web_server()
    log.info("Lessons dir: %s", COURSE_DIR)
    log.info("Lessons found: %d", len(list(COURSE_DIR.glob("*.md"))))

    app = Application.builder().token(BOT_TOKEN).build()

    # Команды пользователя
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("bookmark", bookmark_command))
    app.add_handler(CommandHandler("bookmarks", bookmark_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("health", health))

    # Админ
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # Inline-кнопки и поиск
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

    # Ежедневное напоминание (8:00 по умолчанию)
    if app.job_queue:
        app.job_queue.run_daily(daily_lesson, time=time(hour=8, minute=0))
    else:
        log.warning("Job queue not available — daily reminders disabled. Install python-telegram-bot[job-queue]")

    log.info("Bot started! Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
