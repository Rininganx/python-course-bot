"""
Парсинг Markdown-файлов уроков для Telegram.

Читает .md файлы из lessons/, конвертирует в Telegram-дружелюблный формат,
разбивает длинные уроки на секции по 3900 символов.
Кэширует результат в памяти для повторных запросов.
"""
import re
from pathlib import Path

from .config import COURSE_DIR

_cache: dict[str, dict] = {}


def clean_markdown(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3 :].strip()

    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    for tag in ["tags:", "date:", "status:", "phase:", "topic:", "aliases:", "cssclasses:"]:
        text = re.sub(rf"^{tag}.*$", "", text, flags=re.MULTILINE)

    callout_map = {
        "warning": "⚠️", "tip": "💡", "bug": "🐛", "example": "📝",
        "hint": "💡", "question": "❓", "success": "✅", "abstract": "📋",
        "info": "ℹ️", "danger": "🔥", "note": "📌",
    }
    for name, emoji in callout_map.items():
        text = re.sub(rf">\s*\[!{name}\]\s*(.+)", rf"{emoji} \1", text, flags=re.IGNORECASE)
        text = re.sub(rf"^\s*\[!{name}\]\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(rf"\[!{name}\]\s*", f"{emoji} ", text, flags=re.IGNORECASE)

    text = re.sub(r"\[/![^\]]+\]", "", text)
    text = re.sub(r"\[![^\]]*\]", "", text)

    lines = text.split("\n")
    result = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            result.append(" • ".join(cells))
        else:
            if in_table:
                in_table = False
            result.append(line)
    text = "\n".join(result)

    text = re.sub(r"^---+\s*$", "─" * 20, text, flags=re.MULTILINE)
    text = re.sub(r"```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def split_for_telegram(text: str, max_len: int = 3900) -> list[str]:
    if len(text) <= max_len:
        return [text]
    sections, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            sections.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        sections.append(current.strip())
    return sections


def parse_lesson(filename: str) -> dict | None:
    if filename in _cache:
        return _cache[filename]

    filepath = COURSE_DIR / f"{filename}.md"
    if not filepath.exists():
        return None

    raw = filepath.read_text(encoding="utf-8")
    content = clean_markdown(raw)
    lesson = {"name": filename, "content": content, "sections": split_for_telegram(content)}
    _cache[filename] = lesson
    return lesson
