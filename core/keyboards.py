"""
Inline-клавиатуры для бота.

Все кнопки навигации: главное меню, модули, уроки, тесты,
закладки, настройки. Каждая функция возвращает InlineKeyboardMarkup.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .config import LESSONS_ORDER, MODULES


def _progress_bar(done: int, total: int, size: int = 10) -> str:
    if total == 0:
        return "░" * size
    filled = round(done / total * size)
    return "▓" * filled + "░" * (size - filled)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖  Уроки", callback_data="modules"),
         InlineKeyboardButton("📈  Прогресс", callback_data="progress")],
        [InlineKeyboardButton("▶️  Продолжить", callback_data="continue"),
         InlineKeyboardButton("🔍  Поиск", callback_data="search")],
        [InlineKeyboardButton("🔖  Закладки", callback_data="bookmarks"),
         InlineKeyboardButton("🎲  Случайный", callback_data="random_lesson")],
    ])


def modules_keyboard(user_progress: dict) -> InlineKeyboardMarkup:
    completed = user_progress.get("completed", [])
    buttons = []
    for mi, mod in enumerate(MODULES):
        done = sum(1 for i in mod["indices"] if i in completed)
        total = len(mod["indices"])
        bar = _progress_bar(done, total, 6)
        prefix = "✅" if done == total else "◽" if done == 0 else "🔵"
        buttons.append([InlineKeyboardButton(
            f"{prefix}  {mod['name']}\n      {bar}  {done}/{total}",
            callback_data=f"module_{mi}"
        )])
    buttons.append([InlineKeyboardButton("◀️  Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def module_keyboard(module_idx: int, user_progress: dict) -> InlineKeyboardMarkup:
    mod = MODULES[module_idx]
    completed = user_progress.get("completed", [])
    bookmarks = user_progress.get("bookmarks", [])
    buttons = []
    for idx in mod["indices"]:
        name = LESSONS_ORDER[idx]
        short = name.split(" - ", 1)[1] if " - " in name else name
        if idx in completed:
            icon = "✅"
        elif idx in bookmarks:
            icon = "🔖"
        else:
            icon = "▫️"
        buttons.append([InlineKeyboardButton(
            f"{icon}  {short}", callback_data=f"lesson_{idx}"
        )])
    buttons.append([InlineKeyboardButton("◀️  К модулям", callback_data="modules")])
    return InlineKeyboardMarkup(buttons)


def lessons_keyboard(user_progress: dict) -> InlineKeyboardMarkup:
    buttons = []
    completed = user_progress.get("completed", [])
    for i, name in enumerate(LESSONS_ORDER):
        icon = "✅" if i in completed else "▫️"
        short = name.split(" - ", 1)[1] if " - " in name else name
        buttons.append([InlineKeyboardButton(
            f"{icon}  {short}", callback_data=f"lesson_{i}"
        )])
    buttons.append([InlineKeyboardButton("◀️  Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def lesson_keyboard(lesson_idx: int, total_sections: int, current_section: int, is_bookmarked: bool = False) -> InlineKeyboardMarkup:
    page = f"{current_section + 1}/{total_sections}"

    nav_row = []
    if current_section > 0:
        nav_row.append(InlineKeyboardButton("◀️", callback_data=f"sec_{lesson_idx}_{current_section - 1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {page}", callback_data="noop"))
    if current_section < total_sections - 1:
        nav_row.append(InlineKeyboardButton("▶️", callback_data=f"sec_{lesson_idx}_{current_section + 1}"))
    else:
        nav_row.append(InlineKeyboardButton("✅ Завершить", callback_data=f"done_{lesson_idx}"))

    bm_icon = "🔖" if is_bookmarked else "🏷️"
    bottom_row = [
        InlineKeyboardButton(bm_icon, callback_data=f"bmtoggle_{lesson_idx}"),
        InlineKeyboardButton("◀️ Модули", callback_data="modules"),
    ]
    return InlineKeyboardMarkup([nav_row, bottom_row])
