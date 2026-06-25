"""
Парсинг Markdown-файлов уроков для Telegram.

Конвертирует Obsidian → красивый Telegram Markdown:
  Блоки кода в рамках, callout-боксы, структурированные секции.
"""
import re
from pathlib import Path

from .config import COURSE_DIR

_cache: dict[str, dict] = {}


def clean_markdown(text: str) -> str:
    # ── Frontmatter ──
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].strip()

    # ── Extract code blocks (protect from transformations) ──
    code_blocks = []

    def _save_code(m):
        lang = m.group(1) or ""
        code = m.group(2).strip()
        idx = len(code_blocks)
        code_blocks.append((lang, code))
        return f"\n%%CODE_{idx}%%\n"

    text = re.sub(r"```(\w*)\n(.*?)```", _save_code, text, flags=re.DOTALL)

    # ── Extract inline code (protect from bold conversion) ──
    inline_codes = []

    def _save_inline(m):
        idx = len(inline_codes)
        inline_codes.append(m.group(0))
        return f"%%IC_{idx}%%"

    text = re.sub(r"`[^`]+`", _save_inline, text)

    # ── Wikilinks ──
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # ── Obsidian metadata ──
    for tag in ["tags:", "date:", "status:", "phase:", "topic:", "aliases:", "cssclasses:"]:
        text = re.sub(rf"^{tag}.*$", "", text, flags=re.MULTILINE)

    # ── Callouts → styled boxes ──
    callout_map = {
        "warning": ("⚠️", "ВНИМАНИЕ"),
        "tip": ("💡", "СОВЕТ"),
        "bug": ("🐛", "БАГ"),
        "example": ("📝", "ПРИМЕР"),
        "hint": ("💡", "ПОДСКАЗКА"),
        "question": ("❓", "ВОПРОС"),
        "success": ("✅", "ГОТОВО"),
        "abstract": ("📋", "ВЫВОД"),
        "info": ("ℹ️", "ИНФО"),
        "danger": ("🔥", "ОПАСНО"),
        "note": ("📌", "ЗАМЕТКА"),
    }
    for name, (emoji, label) in callout_map.items():
        text = re.sub(
            rf">\s*\[!{name}\]\s*(.+)",
            rf"{emoji} *{label}*\n└ {_box_line()}\n\1",
            text, flags=re.IGNORECASE
        )
        text = re.sub(rf"^\s*\[!{name}\]\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(rf"\[!{name}\]\s*", f"{emoji} ", text, flags=re.IGNORECASE)

    text = re.sub(r"\[/![^\]]+\]", "", text)
    text = re.sub(r"\[![^\]]*\]", "", text)

    # ── Blockquotes: > text → styled note ──
    def _blockquote(m):
        content = m.group(1).strip()
        return f"💬  _{content}_"
    text = re.sub(r"^>\s?(.+)$", _blockquote, text, flags=re.MULTILINE)

    # ── Headers ──
    def _header(m):
        level = len(m.group(1))
        title = m.group(2).strip()
        if level == 1:
            bar = "═" * min(len(title) + 4, 30)
            return f"\n╔{bar}╗\n║  *{title.upper()}*  ║\n╚{bar}╝"
        return f"\n■  *{title}*"
    text = re.sub(r"^(#{1,3})\s+(.+)$", _header, text, flags=re.MULTILINE)

    # ── Horizontal rules ──
    text = re.sub(r"^─+$|^---+$", "────────────────────────────────", text, flags=re.MULTILINE)
    text = re.sub(r"^─────+\s*$", "────────────────────────────────", text, flags=re.MULTILINE)

    # ── Tables ──
    lines = text.split("\n")
    result = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                result.append("")
            if re.match(r"^\|[\s\-:|]+$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            row = " │ ".join(cells)
            result.append(f"  {row}")
        else:
            if in_table:
                in_table = False
                result.append("")
            result.append(line)
    text = "\n".join(result)

    # ── Bold: **text** → *text* ──
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # ── Ordered lists: 1. → ① etc ──
    list_nums = "①②③④⑤⑥⑦⑧⑨⑩"
    def _list_num(m):
        n = int(m.group(1))
        emoji = list_nums[n - 1] if 1 <= n <= 10 else f"{n}."
        return f"{emoji} "
    text = re.sub(r"^(\d+)\.\s", _list_num, text, flags=re.MULTILINE)

    # ── Clean whitespace ──
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\n+", "", text)
    text = text.strip()

    # ── Restore code blocks ──
    def _restore_code(m):
        idx = int(m.group(1))
        lang, code = code_blocks[idx]
        if lang == "python":
            lines = []
            for line in code.split("\n"):
                if "#" in line and not line.strip().startswith("#"):
                    parts = line.split("#", 1)
                    lines.append(f"{parts[0].rstrip()}  # {parts[1].strip()}")
                else:
                    lines.append(line)
            code = "\n".join(lines)
        box_w = max(len(line) for line in code.split("\n")) if code else 10
        box_w = max(box_w + 2, 20)
        top = "┌" + "─" * box_w + "┐"
        bot = "└" + "─" * box_w + "┘"
        framed = "\n".join(f"│ {line}{' ' * max(0, box_w - len(line) - 1)}│" for line in code.split("\n"))
        return f"\n{top}\n{framed}\n{bot}"

    text = re.sub(r"%%CODE_(\d+)%%", _restore_code, text)

    # ── Restore inline code ──
    def _restore_inline(m):
        return inline_codes[int(m.group(1))]
    text = re.sub(r"%%IC_(\d+)%%", _restore_inline, text)

    # Final cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def _box_line() -> str:
    return "─" * 24


def split_for_telegram(text: str, max_len: int = 3900) -> list[str]:
    if len(text) <= max_len:
        return [text]

    sections = []
    current = ""
    in_code = False

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("┌") or stripped.startswith("└") or stripped.startswith("│"):
            pass  # inside code box, don't split
        elif stripped.startswith("```"):
            in_code = not in_code

        if len(current) + len(line) + 1 > max_len and current.strip() and not in_code:
            sections.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"

    if current.strip():
        sections.append(current.strip())

    # Merge short trailing section
    if len(sections) > 1 and len(sections[-1]) < 400:
        prev = sections[-2]
        if len(prev) + len(sections[-1]) + 2 <= max_len:
            sections[-2] = prev + "\n\n" + sections[-1]
            sections.pop()

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
