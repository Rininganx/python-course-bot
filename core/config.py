"""
Конфигурация бота.

Все константы: токен, пути, список уроков, модули, ID админов.
Читает переменные окружения: TELEGRAM_BOT_TOKEN, ADMIN_IDS.
"""
import os
from pathlib import Path

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN env var!")

BASE_DIR = Path(__file__).resolve().parent.parent
COURSE_DIR = BASE_DIR / "lessons"
DB_FILE = BASE_DIR / "bot.db"

ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]

LESSONS_ORDER = [
    "01 - Арифметика", "02 - Операторы присваивания", "03 - Переменные и типы данных",
    "04 - Ввод и вывод", "05 - Строки", "06 - Условия",
    "07 - Сравнения и булевы операторы", "08 - Цикл for", "09 - Цикл while",
    "10 - break и continue", "11 - Списки", "12 - Словари",
    "13 - Кортежи и множества", "14 - Функции", "15 - Область видимости",
    "16 - Lambda и встроенные функции", "16.5 - try except",
    "17 - Работа с файлами", "18 - Модуль os", "19 - subprocess",
    "20 - Реестр Windows", "20.5 - pip и venv",
    "21 - Процессы и память psutil", "22 - Службы Windows",
    "23 - Планировщик задач", "23.5 - Классы и ООП",
    "24 - Основы GUI tkinter", "25 - CustomTkinter",
    "26 - Дизайн интерфейса", "27 - Многопоточность",
    "28 - PyInstaller", "29 - Установщик", "30 - GitHub и релиз",
    "31 - Веб-скрейпинг", "32 - Работа с API", "33 - Telegram боты",
    "34 - Базы данных", "35 - Автоматизация рутины", "36 - Фриланс и заработок"
]

MODULES = [
    {"name": "🎯 Основы", "desc": "Арифметика — Строки", "indices": [0, 1, 2, 3, 4]},
    {"name": "🧠 Логика", "desc": "Условия — break/continue", "indices": [5, 6, 7, 8, 9]},
    {"name": "📦 Структуры данных", "desc": "Списки — Кортежи", "indices": [10, 11, 12]},
    {"name": "⚡ Функции", "desc": "Функции — try/except", "indices": [13, 14, 15, 16]},
    {"name": "💻 Система", "desc": "Файлы — pip/venv", "indices": [17, 18, 19, 20, 21]},
    {"name": "🔧 Автоматизация", "desc": "psutil — ООП", "indices": [22, 23, 24, 25]},
    {"name": "🖼 GUI", "desc": "tkinter — PyInstaller", "indices": [26, 27, 28, 29, 30]},
    {"name": "🚀 Продвинутое", "desc": "Веб-скрейпинг — Фриланс", "indices": [31, 32, 33, 34, 35, 36, 37, 38]},
]
