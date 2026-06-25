"""
Inline-клавиатуры — кликбейтный дизайн с эмодзи.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .config import LESSONS_ORDER, MODULES

MOD_ICONS = ["🟢", "🔵", "🟣", "🔴", "🟡", "🟠", "⚪", "💎"]
MOD_NAMES_SHORT = [
    "Арифметика, строки",
    "Условия, циклы",
    "Списки, словари",
    "Функции, ошибки",
    "Файлы, системные",
    "Службы, ООП",
    "GUI, интерфейсы",
    "Боты, фриланс",
]


def _pct_bar(done: int, total: int, size: int = 6) -> str:
    if total == 0:
        return "." * size
    filled = round(done / total * size)
    return "█" * filled + "░" * (size - filled)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶  НАЧАТЬ КУРС", callback_data="continue")],
        [InlineKeyboardButton("📚  Модули", callback_data="modules"),
         InlineKeyboardButton("📊  Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton("🔖  Закладки", callback_data="bookmarks"),
         InlineKeyboardButton("🎲  Случайный урок", callback_data="random_lesson")],
        [InlineKeyboardButton("🔍  Поиск темы", callback_data="search"),
         InlineKeyboardButton("⚙️  Настройки", callback_data="settings")],
    ])


def modules_keyboard(user_progress: dict) -> InlineKeyboardMarkup:
    completed = user_progress.get("completed", [])
    buttons = [[InlineKeyboardButton("◀  Назад", callback_data="back_main")]]
    for mi, mod in enumerate(MODULES):
        done = sum(1 for i in mod["indices"] if i in completed)
        total = len(mod["indices"])
        bar = _pct_bar(done, total)
        icon = MOD_ICONS[mi] if mi < len(MOD_ICONS) else "📦"
        desc = MOD_NAMES_SHORT[mi] if mi < len(MOD_NAMES_SHORT) else ""
        if done == total:
            tag = " ✓"
        elif done > 0:
            tag = ""
        else:
            tag = ""
        buttons.append([InlineKeyboardButton(
            f"{icon}  {desc}{tag}\n     {bar}  {done}/{total}",
            callback_data=f"module_{mi}"
        )])
    return InlineKeyboardMarkup(buttons)


def module_keyboard(module_idx: int, user_progress: dict) -> InlineKeyboardMarkup:
    mod = MODULES[module_idx]
    completed = user_progress.get("completed", [])
    bookmarks = user_progress.get("bookmarks", [])
    icon = MOD_ICONS[module_idx] if module_idx < len(MOD_ICONS) else "📦"

    buttons = []
    for i, idx in enumerate(mod["indices"]):
        name = LESSONS_ORDER[idx]
        short = name.split(" - ", 1)[1] if " - " in name else name
        num = f"{i + 1:02d}"
        if idx in completed:
            status = "✅"
        elif idx in bookmarks:
            status = "🔖"
        else:
            status = "📖"
        buttons.append([InlineKeyboardButton(
            f"{status}  {num}. {short}", callback_data=f"lesson_{idx}"
        )])

    done = sum(1 for i in mod["indices"] if i in completed)
    total = len(mod["indices"])
    pct = int(done / total * 100) if total > 0 else 0
    bar = _pct_bar(done, total)
    footer = f"{icon}  {bar}  {pct}%"
    buttons.append([InlineKeyboardButton(footer, callback_data="noop")])
    buttons.append([InlineKeyboardButton("◀  К модулям", callback_data="modules")])
    return InlineKeyboardMarkup(buttons)


def lessons_keyboard(user_progress: dict) -> InlineKeyboardMarkup:
    buttons = []
    completed = user_progress.get("completed", [])
    for i, name in enumerate(LESSONS_ORDER):
        status = "✅" if i in completed else "📖"
        short = name.split(" - ", 1)[1] if " - " in name else name
        buttons.append([InlineKeyboardButton(
            f"{status}  {short}", callback_data=f"lesson_{i}"
        )])
    buttons.append([InlineKeyboardButton("◀  Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def lesson_keyboard(lesson_idx: int, total_sections: int, current_section: int, is_bookmarked: bool = False) -> InlineKeyboardMarkup:
    page = f"{current_section + 1}/{total_sections}"

    nav_row = []
    if current_section > 0:
        nav_row.append(InlineKeyboardButton("◀", callback_data=f"sec_{lesson_idx}_{current_section - 1}"))
    nav_row.append(InlineKeyboardButton(f"📄  {page}", callback_data="noop"))
    if current_section < total_sections - 1:
        nav_row.append(InlineKeyboardButton("▶", callback_data=f"sec_{lesson_idx}_{current_section + 1}"))
    else:
        nav_row.append(InlineKeyboardButton("🎯  Завершить", callback_data=f"done_{lesson_idx}"))

    bm = "🔖  В закладках" if is_bookmarked else "🏷  Добавить"
    bottom_row = [
        InlineKeyboardButton(bm, callback_data=f"bmtoggle_{lesson_idx}"),
        InlineKeyboardButton("◀  Модули", callback_data="modules"),
    ]
    return InlineKeyboardMarkup([nav_row, bottom_row])
