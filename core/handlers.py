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
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Привет, {user.first_name}!\n\n"
        f"  {hero}\n"
        f"  {sub}\n\n"
        f"  [{bar}]  {pct}%\n"
        f"  Уроков: {done}/{total}{streak_line}\n\n"
        f"  {current}"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Команды бота\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "  /start     Главное меню\n"
        "  /stats     Моя статистика\n"
        "  /random    Случайный урок\n"
        "  /bookmark  Мои закладки\n"
        "  /settings  Напоминания\n"
        "  /export    Экспорт прогресса\n\n"
        "Или просто напиши тему для поиска"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_main")]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Сброс прогресса\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Это удалит весь прогресс,\n"
        "закладки и streak.\n\n"
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
        f"ТВОЙ ПРОГРЕСС\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  [{bar}]  {pct}%\n\n"
        f"  Уроков: {done}/{total}\n"
        f"  Streak: {streak} дн.\n"
        f"  Закладки: {bms}\n\n"
        f"  По модулям:\n" + "\n".join(mod_lines)
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_main")]])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    h = progress.get("reminder_h", 8)
    m = progress.get("reminder_m", 0)
    text = (
        f"Настройки\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Напоминание: {h:02d}:{m:02d}\n\n"
        f"Выбери новое время:"
    )
    buttons = []
    for hour in range(6, 23):
        marker = "  << сейчас" if hour == h else ""
        buttons.append([InlineKeyboardButton(
            f"  {hour:02d}:00{marker}", callback_data=f"settime_{hour}_0"
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
    header = f"{name}  |  {page}\n{'-' * 30}\n\n"
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
            f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  {hero}\n"
            f"  {sub}\n\n"
            f"  [{bar}]  {pct}%\n"
            f"  Уроков: {done}/{total}{streak_line}\n\n"
            f"  {current}"
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
