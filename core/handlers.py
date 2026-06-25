"""
Обработчики команд и callback-кнопок бота.

Команды: /start, /help, /stats, /random, /bookmark, /settings, /export, /reset, /health
Админ:   /admin, /broadcast <текст>
Квизы:   тесты в конце уроков (доступны для уроков с определениями в QUIZZES)
Сертификат: выдаётся при прохождении всех уроков
"""
import random
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .config import LESSONS_ORDER, MODULES, COURSE_DIR, ADMIN_IDS
from .storage import (
    get_user_progress, update_user_progress, toggle_bookmark, reset_user,
    get_all_users, set_reminder, save_quiz_result, get_quiz_result,
)
from .lessons import parse_lesson
from .keyboards import (
    main_menu_keyboard, modules_keyboard, module_keyboard,
    lessons_keyboard, lesson_keyboard,
)

log = logging.getLogger(__name__)


# === USER COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    progress = get_user_progress(user.id)
    done = len(progress["completed"])
    total = len(LESSONS_ORDER)
    pct = int(done / total * 100) if total > 0 else 0
    filled = round(pct / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    streak = progress.get("streak", 0)

    if done == 0:
        hero = "Начни изучать Python уже сегодня!"
        sub = "39 уроков от основ до фриланса"
    elif pct < 30:
        hero = f"Отличное начало! Уже {done} уроков за тобой"
        sub = "Продолжай — впереди ещё много интересного"
    elif pct < 70:
        hero = f"Ты в середине пути! {pct}% пройдено"
        sub = f"Осталось {total - done} уроков"
    elif pct < 100:
        hero = f"Почти готово! Осталось {total - done} уроков"
        sub = "Финишная прямая — не останавливайся!"
    else:
        hero = "Курс пройден! Ты — машина!"
        sub = "Попробуй тесты или повтори сложные темы"

    streak_line = f"  {streak} дн. подряд" if streak > 0 else ""
    current = LESSONS_ORDER[progress["current"]] if progress["current"] < len(LESSONS_ORDER) else "Курс пройден!"

    text = (
        f"PYTHON COURSE\n"
        f"────────────────────────\n"
        f"{hero}\n\n"
        f"[{bar}]  {pct}%\n"
        f"Уроков {done}/{total}{streak_line}\n\n"
        f"Текущий: {current}"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "КОМАНДЫ\n"
        "────────────────────────\n"
        "/start - Меню\n"
        "/stats - Прогресс\n"
        "/random - Случайный\n"
        "/bookmark - Закладки\n"
        "/settings - Настройки\n"
        "/export - Экспорт\n\n"
        "Или напиши тему для поиска"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_main")]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Сброс прогресса\n"
        "────────────────────────\n\n"
        "Удалит прогресс, закладки, streak.\n"
        "Ты уверен?"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Да, сбросить", callback_data="reset_yes"),
         InlineKeyboardButton("Нет", callback_data="back_main")]
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    not_done = [i for i in range(len(LESSONS_ORDER)) if i not in progress["completed"]]
    if not not_done:
        await update.message.reply_text("Все уроки пройдены!", reply_markup=main_menu_keyboard())
        return
    idx = random.choice(not_done)
    name = LESSONS_ORDER[idx]
    short = name.split(" - ", 1)[1] if " - " in name else name
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{short}", callback_data=f"lesson_{idx}")],
        [InlineKeyboardButton("Ещё раз", callback_data="random_lesson")]
    ])
    await update.message.reply_text(f"Случайный урок:\n\n{name}", reply_markup=kb, parse_mode="Markdown")


async def bookmark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    bms = progress.get("bookmarks", [])
    if not bms:
        await update.message.reply_text(
            "┌─────────────────────────┐\n"
            "│  🔖  Закладки              │\n"
            "└─────────────────────────┘\n\n"
            "Пока пусто.\nОткрой урок и нажми 🔖 чтобы добавить.",
            parse_mode="Markdown"
        )
        return
    text = f"┌─────────────────────────┐\n│  🔖  Закладки  ({len(bms)})        │\n└─────────────────────────┘\n"
    buttons = []
    for idx in bms:
        name = LESSONS_ORDER[idx] if idx < len(LESSONS_ORDER) else f"Урок {idx}"
        short = name.split(" - ", 1)[1] if " - " in name else name
        buttons.append([InlineKeyboardButton(f"📖  {short}", callback_data=f"lesson_{idx}")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    done = len(progress["completed"])
    total = len(LESSONS_ORDER)
    pct = int(done / total * 100) if total > 0 else 0
    filled = round(pct / 5)
    bar = "▓" * filled + "░" * (20 - filled)
    streak = progress.get("streak", 0)
    bms = len(progress.get("bookmarks", []))

    mod_lines = []
    for mi, mod in enumerate(MODULES):
        mod_done = sum(1 for i in mod["indices"] if i in progress["completed"])
        mod_total = len(mod["indices"])
        mod_pct = int(mod_done / mod_total * 100) if mod_total > 0 else 0
        mod_filled = round(mod_pct / 8)
        mod_bar = "▓" * mod_filled + "░" * (8 - mod_filled)
        if mod_done == mod_total:
            status = "DONE"
        elif mod_done > 0:
            status = f"{mod_done}/{mod_total}"
        else:
            status = "—"
        mod_lines.append(f"  {mod_bar}  {status}")

    text = (
        f"МОЙ ПРОГРЕСС\n"
        f"────────────────────────\n"
        f"[{bar}]  {pct}%\n\n"
        f"Уроков {done}/{total}\n"
        f"Streak {streak} дн.\n"
        f"Закладки {bms}\n\n"
        + "\n".join(mod_lines)
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_main")]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    h = progress.get("reminder_h", 8)
    text = (
        f"НАСТРОЙКИ\n"
        f"────────────────────────\n"
        f"Напоминание: {h:02d}:00\n\n"
        f"Выбери время:"
    )
    buttons = []
    for hour in range(6, 23):
        marker = " <<" if hour == h else ""
        buttons.append([InlineKeyboardButton(
            f"{hour:02d}:00{marker}", callback_data=f"settime_{hour}_0"
        )])
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_main")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    done = len(progress["completed"])
    total = len(LESSONS_ORDER)
    pct = int(done / total * 100) if total > 0 else 0

    lines = [
        f"📊 Экспорт прогресса — {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Пройдено: {done}/{total} ({pct}%)",
        f"Streak: {progress.get('streak', 0)} дн.",
        f"Начато: {progress.get('started', 'N/A')[:10]}",
        "",
        "=== Пройденные уроки ===",
    ]
    for idx in sorted(progress["completed"]):
        name = LESSONS_ORDER[idx] if idx < len(LESSONS_ORDER) else f"Урок {idx}"
        lines.append(f"  ✅ {name}")

    lines.append("")
    lines.append("=== Закладки ===")
    for idx in progress.get("bookmarks", []):
        name = LESSONS_ORDER[idx] if idx < len(LESSONS_ORDER) else f"Урок {idx}"
        lines.append(f"  🔖 {name}")

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n... (обрезано)"
    await update.message.reply_text(f"```\n{text}\n```", parse_mode="Markdown")


async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lessons_count = len(list(COURSE_DIR.glob("*.md")))
    users = get_all_users()
    await update.message.reply_text(
        f"✅ Бот работает!\n"
        f"Уроков в базе: {lessons_count}\n"
        f"Пользователей: {len(users)}\n"
        f"Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )


# === ADMIN ===

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    total = len(users)
    active = sum(1 for u in users if u.get("last_active"))
    completed = sum(1 for u in users if len(u.get("completed", [])) >= len(LESSONS_ORDER))

    text = (
        f"┌─────────────────────────┐\n"
        f"│  🛠  Админ-панель          │\n"
        f"└─────────────────────────┘\n\n"
        f"  ▸ Пользователей:  👤 *{total}*\n"
        f"  ▸ Активных:       🟢 *{active}*\n"
        f"  ▸ Закончили:      🎓 *{completed}*\n\n"
        f"  /broadcast <текст>  —  Рассылка"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤  Рассылка", callback_data="admin_broadcast")]
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Использование: /broadcast <текст сообщения>")
        return
    text = " ".join(context.args)
    users = get_all_users()
    sent, failed = 0, 0
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["user_id"],
                text=f"📢 *Объявление*\n\n{text}",
                parse_mode="Markdown",
            )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"✅ Отправлено: {sent}\n❌ Ошибки: {failed}")


# === LESSON DISPLAY ===

async def send_lesson(query, context, lesson_idx: int, section: int, user_id: int):
    if lesson_idx < 0 or lesson_idx >= len(LESSONS_ORDER):
        await query.edit_message_text("❌ Урок не найден.")
        return

    name = LESSONS_ORDER[lesson_idx]
    lesson = parse_lesson(name)
    if not lesson:
        await query.edit_message_text(f"❌ Урок не найден: {name}")
        return

    update_user_progress(user_id, lesson_idx)
    progress = get_user_progress(user_id)
    sections = lesson["sections"]
    if section >= len(sections):
        section = len(sections) - 1
    page = f"{section + 1}/{len(sections)}"
    done_count = len(progress.get("completed", []))
    total = len(LESSONS_ORDER)
    header = f"{name}  |  {page}\n────────────────────────\n\n"
    text = header + sections[section]
    is_bm = lesson_idx in progress.get("bookmarks", [])

    try:
        await query.edit_message_text(
            text,
            reply_markup=lesson_keyboard(lesson_idx, len(sections), section, is_bm),
            parse_mode="Markdown",
        )
    except Exception:
        try:
            plain = text.replace("*", "").replace("`", "").replace("_", " ")
            await query.edit_message_text(
                plain,
                reply_markup=lesson_keyboard(lesson_idx, len(sections), section, is_bm),
            )
        except Exception:
            log.warning("Failed to send lesson %d section %d", lesson_idx, section)


# === CHEAT SHEETS ===

CHEATS = {
    0: """Арифметика — шпаргалка
────────────────────────
+   сложение
-   вычитание
*   умножение
/   деление (float)
//  целочисленное деление
%   остаток от деления
**  степень

Порядок: ** > * / // % > + -
Скобки () меняют порядок""",

    1: """Операторы присваивания
────────────────────────
x = 5     присваивание
x += 3    x = x + 3
x -= 3    x = x - 3
x *= 3    x = x * 3
x /= 3    x = x / 3
x //= 3   x = x // 3
x %= 3    x = x % 3
x **= 3   x = x ** 3""",

    2: """Типы данных
────────────────────────
int     целые: 42, -7, 0
float   дробные: 3.14, -0.5
str     строки: "hello", 'world'
bool    True / False

type(x)       тип переменной
int("42")     str -> int
str(42)       int -> str
float("3.14") str -> float
bool(0)       False, bool(1) True""",

    3: """Ввод и вывод
────────────────────────
print("hello")        вывод
print(a, b, sep=", ") разделитель
print(a, end=" ")     без переноса

f-строки:
f"{x}"          значение
f"{x:.2f}"      2 знака после запятой
f"{x:>10}"      выравнивание вправо
f"{x:<10}"      выравнивание влево
f"{x:^10}"      по центру
f"{x:%}"        процент

input("Вопрос: ")  ввод с клавиатуры""",

    4: """Строки — шпаргалка
────────────────────────
len(s)           длина
s[i]             символ по индексу
s[a:b]           срез
s[::-1]          реверс

Методы:
upper() / lower()   регистр
strip()             убрать пробелы
split(",")          разделить
" ".join(list)      объединить
replace("a", "b")   замена
find("x")           позиция (или -1)
count("x")          сколько раз
center(10)          по центру
ljust(10) / rjust() выравнивание""",

    5: """Условия
────────────────────────
if условие:
    код
elif условие:
    код
else:
    код

Тернарник:
x = значение if условие else другое

Pass — пустой блок:
if True:
    pass

Truthiness:
False, 0, "", [], {}, None — ложь
Всё остальное — истина""",

    6: """Сравнения и логика
────────────────────────
==  равно        !=  не равно
>   больше       <  меньше
>=  больше=      <=  меньше=

in / not in      принадлежность
is / is not       ссылка

and  и           or  или
not  не

Кортежи сравнений:
1 < x < 10  ==  (1 < x) and (x < 10)""",

    7: """Цикл for
────────────────────────
for i in range(5):     0,1,2,3,4
for i in range(1,6):   1,2,3,4,5
for i in range(0,10,2): 0,2,4,6,8

for s in "hello":      по символам
for x in [1,2,3]:      по элементам

enumerate(list)    индекс + значение
zip(a, b)          параллельно

Список:
[x**2 for x in range(10)]
[x for x in list if x > 0]""",

    8: """Цикл while
────────────────────────
while условие:
    код

无限循环:
while True:
    break

Счётчик:
n = 0
while n < 10:
    n += 1

Проверка ввода:
while True:
    x = input()
    if x.isdigit():
        break""",

    9: """break и continue
────────────────────────
break    выход из цикла
continue пропуск итерации

Флаг:
found = False
for x in list:
    if x == target:
        found = True
        break

for...else:
for x in list:
    if x == target:
        break
else:
    print("Не найдено")""",

    10: """Списки — шпаргалка
────────────────────────
lst = [1, 2, 3]
lst[i]         элемент
lst[a:b]       срез
len(lst)       длина

Методы:
append(x)      добавить в конец
insert(i, x)   вставить по индексу
extend(list)   добавить список
remove(x)      удалить значение
pop(i)         удалить по индексу
sort()         сортировка
reverse()      реверс
copy()         копия

[x**2 for x in lst]    генератор
[x for x in lst if x>0] с фильтром""",

    11: """Словари — шпаргалка
────────────────────────
d = {"key": "value"}
d["key"]          значение
d.get("key", 0)   безопасно

Методы:
keys()     ключи
values()   значения
items()    пары
update(d2) обновить
pop(key)   удалить

Генератор:
{x: x**2 for x in range(5)}

Вложенность:
users = {
    "name": "Ivan",
    "age": 25
}""",

    12: """Кортежи и множества
────────────────────────
t = (1, 2, 3)     кортеж (неизменяемый)
a, b, c = (1, 2, 3)  распаковка
a, b = b, a       swap

s = {1, 2, 3}     множество (уникальные)
s & s2   пересечение
s | s2   объединение
s - s2   разность
s ^ s2   симметрическая разность

list(set(lst))  удалить дубликаты""",

    13: """Функции — шпаргалка
────────────────────────
def имя(аргументы):
    return значение

Параметры:
def f(a, b=10)       по умолчанию
def f(*args)         позиционные
def f(**kwargs)      именованные
def f(a, /, b)       только позиционные

def f(x: int) -> str  подсказка типов
\"\"\"docstring\"\"\"      документация

return a, b  вернёт кортеж""",

    14: """Область видимости
────────────────────────
x = 1          глобальная

def f():
    x = 2     локальная

def f():
    global x  изменить глобальную

def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2

LEGB: Local -> Enclosing -> Global -> Built-in""",

    15: """Lambda и встроенные
────────────────────────
lambda x: x + 1        анонимная
lambda x, y: x + y     с 2 аргументами

sorted(lst, key=lambda x: x[1])
map(func, lst)          применить
filter(func, lst)       отфильтровать

Встроенные:
sum(lst)   min(lst)   max(lst)
len(lst)   abs(x)     round(x, 2)
any(lst)   all(lst)
reversed(lst)""",

    16: """try/except — шпаргалка
────────────────────────
try:
    код
except ValueError as e:
    ошибка
else:
    если ошибок не было
finally:
    всегда

except (TypeError, ValueError):
    несколько ошибок

raise ValueError("msg")
    выбросить ошибку

except:
    перехватить всё (осторожно!)""",

    17: """Файлы — шпаргалка
────────────────────────
with open("f.txt") as f:
    data = f.read()      всё
    lines = f.readlines() список строк
    for line in f:        построчно

with open("f.txt", "w") as f:
    f.write("text")

with open("f.txt", "a") as f:
    f.write("text")      дописать

import json
json.dump(obj, f)
json.load(f)""",

    18: """Модуль os — шпаргалка
────────────────────────
import os, os.path

os.getcwd()              текущая папка
os.listdir(".")          содержимое
os.makedirs("a/b")       создать папки
os.rename("a", "b")      переименовать
os.remove("f.txt")       удалить файл

os.path.exists("f")      существует?
os.path.isfile("f")      файл?
os.path.isdir("d")       папка?
os.path.join("a", "b")   соединить пути
os.path.getsize("f")     размер

os.environ["KEY"]        переменные""",

    19: """subprocess — шпаргалка
────────────────────────
import subprocess

r = subprocess.run(
    ["cmd", "/c", "dir"],
    capture_output=True,
    text=True
)
print(r.stdout)

Для PowerShell:
r = subprocess.run(
    ["powershell", "-c", "Get-Process"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)""",

    20: """Реестр Windows
────────────────────────
import winreg

key = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    "Software\\...",
    0, winreg.KEY_READ
)
value, _ = winreg.QueryValueEx(key, "Name")
winreg.CloseKey(key)

Запись:
key = winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(key, "Name", 0, winreg.REG_SZ, "value")""",

    21: """pip и venv
────────────────────────
pip install package
pip install package==1.0
pip install -r requirements.txt
pip freeze > requirements.txt

python -m venv .venv
.venv\\Scripts\\activate     Windows
source .venv/bin/activate   Linux/Mac
deactivate

pip list                список
pip show package        инфо""",

    22: """psutil — шпаргалка
────────────────────────
import psutil

psutil.cpu_percent()    загрузка CPU
psutil.cpu_count()      ядра

psutil.virtual_memory() RAM
psutil.disk_partitions() диски
psutil.net_io_counters() сеть

psutil.pids()           процессы
psutil.Process(pid)     процесс

psutil.sensors_temperatures()  температура""",

    23: """Службы Windows
────────────────────────
sc query               список
sc start "name"        запустить
sc stop "name"         остановить
sc config "name" start=auto

import psutil
for s in psutil.win_service_iter():
    print(s.name(), s.status())""",

    24: """Планировщик задач
────────────────────────
schtasks /query        список
schtasks /create /tn "name" /tr "cmd" /sc daily /st 09:00
schtasks /delete /tn "name" /f
schtasks /run /tn "name"

Триггеры:
ONLOGON   при входе
ONSTART   при старте
DAILY     ежедневно
WEEKLY    еженедельно""",

    25: """Классы и ООП
────────────────────────
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says Woof!"

class Puppy(Dog):
    def bark(self):
        return f"{self.name} says Yip!"

Магические методы:
__str__    str(obj)
__len__    len(obj)
__add__    obj1 + obj2""",

    26: """tkinter — шпаргалка
────────────────────────
from tkinter import *

root = Tk()
root.title("Window")
root.geometry("400x300")

Label(root, text="Hi").pack()
Button(root, text="Click").pack()
Entry(root).pack()
Text(root).pack()

root.mainloop()

pack()    simple
grid()    table
place()   absolute""",

    27: """CustomTkinter
────────────────────────
import customtkinter as ctk

ctk.set_appearance_mode("dark")
root = ctk.CTk()

ctk.CTkLabel(root, text="Hi").pack()
ctk.CTkButton(root, text="Click").pack()
ctk.CTkEntry(root).pack()
ctk.CTkSlider(root).pack()
ctk.CTkProgressBar(root).pack()""",

    28: """Многопоточность
────────────────────────
import threading

def task():
    print("Running...")

t = threading.Thread(target=task, daemon=True)
t.start()

# НЕ обновлять GUI из потока!
# Использовать root.after() или Queue""",

    29: """PyInstaller
────────────────────────
pip install pyinstaller

pyinstaller --onefile script.py
pyinstaller --onefile --windowed app.py

Спек-файл:
pyinstaller --onefile --add-data "data;." script.py

# Скрипт сборки
pyinstaller build.spec""",

    30: """Установщик (Inno Setup)
────────────────────────
[Setup]
AppName=MyApp
AppVersion=1.0
DefaultDirName={autopf}\MyApp

[Files]
Source: "dist\app.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\MyApp"; Filename: "{app}\app.exe"
Name: "{autodesktop}\MyApp"; Filename: "{app}\app.exe" """,

    31: """Git — шпаргалка
────────────────────────
git init
git add .
git commit -m "msg"
git push
git pull

git status
git log --oneline
git diff

git branch feature
git checkout feature
git merge feature

.gitexcept:
__pycache__/
.venv/
*.exe""",

    32: """Веб-скрейпинг
────────────────────────
import requests
from bs4 import BeautifulSoup

r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

soup.find("div", class_="name")
soup.select("div > p")
soup.get_text()""",

    33: """Работа с API
────────────────────────
import requests

r = requests.get(url, headers={"key": "val"})
r = requests.post(url, json={"key": "val"})
data = r.json()

# Ретраи
for i in range(3):
    try:
        r = requests.get(url, timeout=5)
        break
    except:
        time.sleep(2**i)""",

    34: """Telegram боты
────────────────────────
from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("Hi!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()""",

    35: """SQLite — шпаргалка
────────────────────────
import sqlite3

conn = sqlite3.connect("db.db")
conn.row_factory = sqlite3.Row

conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("INSERT INTO t VALUES (?, ?)", (1, "name"))
conn.commit()

rows = conn.execute("SELECT * FROM t").fetchall()
for r in rows:
    print(r["name"])

conn.close()""",

    36: """Автоматизация — шпаргалка
────────────────────────
# Excel
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws["A1"] = "Hello"
wb.save("file.xlsx")

# PDF
from PyPDF2 import PdfReader
r = PdfReader("file.pdf")
text = r.pages[0].extract_text()

# Email
import smtplib
s = smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()
s.login("user", "pass")""",
}


async def cheat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    idx = int(data.split("_")[1])

    if idx not in CHEATS:
        await query.answer("Шпаргалка не найдена", show_alert=True)
        return

    text = CHEATS[idx]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀  К уроку", callback_data=f"lesson_{idx}")],
        [InlineKeyboardButton("◀  Модули", callback_data="modules")],
    ])
    await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")


# === QUIZ ===

QUIZZES = {
    0: [
        {"q": "Чему равно 10 // 3?", "options": ["3", "3.33", "4", "3.0"], "answer": 0},
        {"q": "Что делает оператор %?", "options": ["Процент", "Остаток от деления", "Деление", "Модуль"], "answer": 1},
        {"q": "6 ** 3 = ?", "options": ["18", "216", "36", "63"], "answer": 1},
    ],
    2: [
        {"q": "Какой тип у переменной x = 5?", "options": ["str", "float", "int", "bool"], "answer": 2},
        {"q": "type('hello') вернёт?", "options": ["str", "String", "text", "char"], "answer": 0},
    ],
    5: [
        {"q": "Какая конструкция для условия?", "options": ["for", "while", "if", "def"], "answer": 2},
        {"q": "elif — это сокращение от?", "options": ["else if", "else inside", "end if", "early if"], "answer": 0},
    ],
    7: [
        {"q": "range(5) создаёт числа?", "options": ["0-5", "1-5", "0-4", "1-4"], "answer": 2},
        {"q": "for i in range(3): print(i) выведет?", "options": ["1,2,3", "0,1,2", "0,1,2,3", "1,2"], "answer": 1},
    ],
    10: [
        {"q": "Что делает break?", "options": ["Пауза", "Выход из цикла", "Пропуск итерации", "Рестарт"], "answer": 1},
        {"q": "Что делает continue?", "options": ["Выход", "Пауза", "Пропуск итерации", "Стоп"], "answer": 2},
    ],
    13: [
        {"q": "def — это ключевое слово для?", "options": ["Переменной", "Функции", "Класса", "Модуля"], "answer": 1},
        {"q": "Что вернёт функция без return?", "options": ["0", "None", "False", "Пустоту"], "answer": 1},
    ],
    16: [
        {"q": "lambda — это?", "options": ["Функция", "Переменная", "Модуль", "Класс"], "answer": 0},
        {"q": "len([1,2,3]) вернёт?", "options": ["2", "3", "4", "6"], "answer": 1},
    ],
    17: [
        {"q": "open('f.txt', 'r') — это?", "options": ["Запись", "Чтение", "Создание", "Удаление"], "answer": 1},
    ],
    23: [
        {"q": "class — это?", "options": ["Функция", "Переменная", "Шаблон объекта", "Модуль"], "answer": 2},
        {"q": "self в методе — это?", "options": ["Класс", "Текущий объект", "Модуль", "None"], "answer": 1},
    ],
}


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, lesson_idx: int, user_id: int):
    if lesson_idx not in QUIZZES:
        return
    quiz = QUIZZES[lesson_idx]
    context.user_data["quiz"] = {"lesson_idx": lesson_idx, "questions": quiz, "current": 0, "score": 0}
    await _send_quiz_question(update, context, user_id)


async def _send_quiz_question(update, context, user_id):
    quiz = context.user_data.get("quiz")
    if not quiz:
        return
    q_idx = quiz["current"]
    if q_idx >= len(quiz["questions"]):
        await _finish_quiz(update, context, user_id)
        return
    q = quiz["questions"][q_idx]
    buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{i}")] for i, opt in enumerate(q["options"])]
    text = (
        f"📝 *Тест — вопрос {q_idx + 1}/{len(quiz['questions'])}*\n\n"
        f"{q['q']}\n\n"
        f"Счёт: {quiz['score']}/{len(quiz['questions'])}"
    )
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def _finish_quiz(update, context, user_id):
    quiz = context.user_data.pop("quiz", None)
    if not quiz:
        return
    score = quiz["score"]
    total = len(quiz["questions"])
    save_quiz_result(user_id, quiz["lesson_idx"], score, total)

    pct = int(score / total * 100)
    if pct >= 80:
        emoji = "🎉"
        msg = "Отлично!"
    elif pct >= 50:
        emoji = "👍"
        msg = "Неплохо!"
    else:
        emoji = "📚"
        msg = "Стоит повторить урок."

    text = (
        f"{emoji} *Тест завершён!*\n\n"
        f"Счёт: {score}/{total} ({pct}%)\n"
        f"{msg}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data=f"quiz_{quiz['lesson_idx']}")],
        [InlineKeyboardButton("🔙 К модулям", callback_data="modules")]
    ])
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


# === CERTIFICATE ===

async def check_certificate(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    progress = get_user_progress(user_id)
    if len(progress["completed"]) < len(LESSONS_ORDER):
        return
    quiz_scores = []
    for idx in range(len(LESSONS_ORDER)):
        r = get_quiz_result(user_id, idx)
        if r:
            quiz_scores.append(r["score"] / r["total"])
    avg = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0

    text = (
        "🎓 *СЕРТИФИКАТ*\n\n"
        f"Поздравляем! Вы прошли весь курс Python!\n\n"
        f"📅 Дата: {datetime.now().strftime('%d.%m.%Y')}\n"
        f"📊 Уроков: {len(LESSONS_ORDER)}/{len(LESSONS_ORDER)}\n"
        f"📝 Средний балл тестов: {int(avg * 100)}%\n\n"
        f"Курс: Python от основ до фриланса\n"
        f"Уровень: {'Продвинутый' if avg >= 0.8 else 'Базовый'}"
    )
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")


# === DAILY REMINDER ===

async def daily_lesson(context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    for u in users:
        try:
            idx = u["current"]
            if idx >= len(LESSONS_ORDER):
                continue
            name = LESSONS_ORDER[idx]
            text = (
                f"🌅 *Доброе утро!*\n\n"
                f"Сегодняшний урок: *{name}*\n"
                f"Прогресс: {len(u['completed'])}/{len(LESSONS_ORDER)}"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Начать урок", callback_data=f"lesson_{idx}")],
                [InlineKeyboardButton("📊 Прогресс", callback_data="progress")]
            ])
            await context.bot.send_message(chat_id=u["user_id"], text=text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            log.warning("Failed to send daily lesson to %s", u["user_id"])


# === SEARCH ===

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text.lower()
    results = []
    for i, name in enumerate(LESSONS_ORDER):
        if query_text in name.lower():
            results.append((i, name))
        else:
            lesson = parse_lesson(name)
            if lesson and query_text in lesson["content"].lower():
                results.append((i, name))
    if not results:
        await update.message.reply_text("❌ Ничего не найдено.")
        return
    buttons = [[InlineKeyboardButton(f"📖  {name}", callback_data=f"lesson_{idx}")] for idx, name in results[:10]]
    buttons.append([InlineKeyboardButton("◀️  Назад", callback_data="back_main")])
    await update.message.reply_text(f"🔍  Найдено: *{len(results)}*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


# === CALLBACK HANDLER ===

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    progress = get_user_progress(user_id)
    data = query.data

    try:
        await _handle_button(query, context, user_id, progress, data)
    except Exception as e:
        log.error("Button error: %s", e)
        try:
            await query.edit_message_text("⚠️ Ошибка. Попробуй ещё раз.", reply_markup=main_menu_keyboard())
        except Exception:
            pass


async def _handle_button(query, context, user_id, progress, data):
    if data == "back_main":
        done = len(progress["completed"])
        total = len(LESSONS_ORDER)
        pct = int(done / total * 100) if total > 0 else 0
        filled = round(pct / 10)
        bar = "▓" * filled + "░" * (10 - filled)
        streak = progress.get("streak", 0)
        if done == 0:
            hero = "Начни изучать Python уже сегодня!"
            sub = "39 уроков от основ до фриланса"
        elif pct < 30:
            hero = f"Отличное начало! Уже {done} уроков"
            sub = "Продолжай — впереди ещё много интересного"
        elif pct < 70:
            hero = f"Ты в середине пути! {pct}% пройдено"
            sub = f"Осталось {total - done} уроков"
        elif pct < 100:
            hero = f"Почти готово! Осталось {total - done} уроков"
            sub = "Финишная прямая!"
        else:
            hero = "Курс пройден! Ты — машина!"
            sub = "Попробуй тесты или повтори сложные темы"
        streak_line = f"  {streak} дн. подряд" if streak > 0 else ""
        current = LESSONS_ORDER[progress["current"]] if progress["current"] < len(LESSONS_ORDER) else "Курс пройден!"
        text = (
            f"PYTHON COURSE\n"
            f"────────────────────────\n"
            f"{hero}\n\n"
            f"[{bar}]  {pct}%\n"
            f"Уроков {done}/{total}{streak_line}\n\n"
            f"Текущий: {current}"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

    elif data == "modules":
        await query.edit_message_text("┌─────────────────────────┐\n│  📚  Модули                │\n└─────────────────────────┘", reply_markup=modules_keyboard(progress), parse_mode="Markdown")

    elif data == "lessons":
        await query.edit_message_text("📚 *Список уроков:*", reply_markup=lessons_keyboard(progress), parse_mode="Markdown")

    elif data.startswith("module_"):
        mi = int(data.split("_")[1])
        if mi < 0 or mi >= len(MODULES):
            return
        mod = MODULES[mi]
        await query.edit_message_text(
            f"{mod['name']}* — {mod['desc']}*",
            reply_markup=module_keyboard(mi, progress), parse_mode="Markdown"
        )

    elif data == "progress":
        done = len(progress["completed"])
        total = len(LESSONS_ORDER)
        pct = int(done / total * 100) if total > 0 else 0
        filled = round(pct / 5)
        bar = "▓" * filled + "░" * (20 - filled)
        streak = progress.get("streak", 0)
        streak_text = f"  🔥 {streak} дн." if streak > 0 else ""
        mod_lines = []
        for mod in MODULES:
            mod_done = sum(1 for i in mod["indices"] if i in progress["completed"])
            mod_total = len(mod["indices"])
            mod_pct = int(mod_done / mod_total * 100) if mod_total > 0 else 0
            mod_filled = round(mod_pct / 10)
            mod_bar = "▓" * mod_filled + "░" * (10 - mod_filled)
            status = "✅" if mod_done == mod_total else f"{mod_done}/{mod_total}"
            mod_lines.append(f"  {mod['name']}\n  {mod_bar}  {status}")
        text = (
            f"┌─────────────────────────┐\n"
            f"│  📈  Прогресс              │\n"
            f"└─────────────────────────┘\n\n"
            f"  ▸ [{bar}]  *{pct}%*\n"
            f"  ▸ Уроков: *{done}/{total}*{streak_text}\n"
            f"  ▸ Начато: _{progress.get('started', 'N/A')[:10]}_\n\n"
            + "\n\n".join(mod_lines)
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️  Назад", callback_data="back_main")]]),
            parse_mode="Markdown"
        )

    elif data == "continue":
        idx = progress["current"]
        if idx >= len(LESSONS_ORDER):
            await query.edit_message_text("🎉 Все уроки пройдены!", reply_markup=main_menu_keyboard())
            return
        await send_lesson(query, context, idx, 0, user_id)

    elif data.startswith("lesson_"):
        parts = data.split("_")
        if len(parts) < 2:
            return
        idx = int(parts[1])
        await send_lesson(query, context, idx, 0, user_id)

    elif data.startswith("sec_"):
        parts = data.split("_")
        if len(parts) < 3:
            return
        await send_lesson(query, context, int(parts[1]), int(parts[2]), user_id)

    elif data.startswith("done_"):
        parts = data.split("_")
        if len(parts) < 2:
            return
        idx = int(parts[1])
        update_user_progress(user_id, idx, completed=True)
        progress = get_user_progress(user_id)

        has_quiz = idx in QUIZZES
        next_idx = idx + 1
        all_done = len(progress["completed"]) >= len(LESSONS_ORDER)

        buttons = []
        if has_quiz:
            buttons.append([InlineKeyboardButton("Пройти тест", callback_data=f"quiz_{idx}")])
        if next_idx < len(LESSONS_ORDER):
            update_user_progress(user_id, next_idx)
            buttons.append([InlineKeyboardButton("Следующий урок", callback_data=f"lesson_{next_idx}")])
        if all_done:
            buttons.append([InlineKeyboardButton("Сертификат", callback_data="certificate")])
        buttons.append([InlineKeyboardButton("< К модулям", callback_data="modules")])

        text = f"Урок завершен!\n\n{LESSONS_ORDER[idx]}"
        if all_done:
            text += "\n\nПоздравляю! Ты прошел весь курс!"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif data == "search":
        await query.edit_message_text(
            "🔍  Напиши тему для поиска:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️  Назад", callback_data="back_main")]])
        )

    elif data == "random_lesson":
        not_done = [i for i in range(len(LESSONS_ORDER)) if i not in progress["completed"]]
        if not not_done:
            await query.edit_message_text("🎉 Все уроки пройдены!", reply_markup=main_menu_keyboard())
            return
        idx = random.choice(not_done)
        await send_lesson(query, context, idx, 0, user_id)

    elif data == "bookmarks":
        bms = progress.get("bookmarks", [])
        if not bms:
            text = (
                "┌─────────────────────────┐\n"
                "│  🔖  Закладки              │\n"
                "└─────────────────────────┘\n\n"
                "Пока пусто.\nНажми 🔖 на уроке чтобы добавить."
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️  Назад", callback_data="back_main")]])
        else:
            text = f"┌─────────────────────────┐\n│  🔖  Закладки  ({len(bms)})        │\n└─────────────────────────┘\n"
            buttons = []
            for idx in bms:
                name = LESSONS_ORDER[idx] if idx < len(LESSONS_ORDER) else f"Урок {idx}"
                short = name.split(" - ", 1)[1] if " - " in name else name
                buttons.append([InlineKeyboardButton(f"📖  {short}", callback_data=f"lesson_{idx}")])
            buttons.append([InlineKeyboardButton("◀️  Назад", callback_data="back_main")])
            kb = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

    elif data.startswith("bmtoggle_"):
        parts = data.split("_")
        if len(parts) < 2:
            return
        idx = int(parts[1])
        msg = toggle_bookmark(user_id, idx)
        await query.answer(msg, show_alert=True)
        return

    elif data.startswith("quiz_") and data != "quiz_done":
        parts = data.split("_")
        if len(parts) < 2:
            return
        q_idx = int(parts[1])

        quiz = context.user_data.get("quiz")
        if quiz and quiz.get("lesson_idx") == q_idx:
            pass
        else:
            context.user_data["quiz"] = {
                "lesson_idx": q_idx,
                "questions": QUIZZES[q_idx],
                "current": 0,
                "score": 0,
            }
            quiz = context.user_data["quiz"]

        q = quiz["questions"][quiz["current"]]
        selected = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else -1

        if selected >= 0 and quiz["current"] < len(quiz["questions"]):
            q_data = quiz["questions"][quiz["current"]]
            if selected == q_data["answer"]:
                quiz["score"] += 1
            quiz["current"] += 1
            await _send_quiz_question(query, context, user_id)
        return

    elif data.startswith("settime_"):
        parts = data.split("_")
        if len(parts) < 3:
            return
        hour = int(parts[1])
        minute = int(parts[2])
        set_reminder(user_id, hour, minute)
        await query.answer(f"⏰ Напоминание установлено на {hour:02d}:{minute:02d}", show_alert=True)
        return

    elif data == "certificate":
        await check_certificate(user_id, context)
        return

    elif data == "settings":
        h = progress.get("reminder_h", 8)
        m = progress.get("reminder_m", 0)
        text = f"⚙️ *Настройки*\n\n⏰ Напоминание: {h:02d}:{m:02d}"
        buttons = []
        for hour in range(6, 23):
            buttons.append([InlineKeyboardButton(f"⏰ {hour:02d}:00", callback_data=f"settime_{hour}_0")])
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_main")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif data == "reset_confirm":
        text = (
            "⚠️ *Сброс прогресса*\n\n"
            "Это удалит весь прогресс, закладки и streak.\n"
            "Ты уверен?"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Да, сбросить", callback_data="reset_yes"),
             InlineKeyboardButton("✅ Нет", callback_data="back_main")]
        ])
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

    elif data == "reset_yes":
        reset_user(user_id)
        await query.edit_message_text(
            "✅  Прогресс сброшен!\nНачинаем заново 🚀",
            reply_markup=main_menu_keyboard()
        )
