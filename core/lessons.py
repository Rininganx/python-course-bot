"""
Парсинг Markdown-файлов уроков для Telegram.

Новый формат: простой Markdown без Obsidian syntax.
Код в ```, заголовки #, буллеты -.
"""
import re
from pathlib import Path

from .config import COURSE_DIR

_cache: dict[str, dict] = {}


def clean_markdown(text: str) -> str:
    # ── Frontmatter (legacy) ──
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

    # ── Extract inline code ──
    inline_codes = []

    def _save_inline(m):
        idx = len(inline_codes)
        inline_codes.append(m.group(0))
        return f"%%IC_{idx}%%"

    text = re.sub(r"`[^`]+`", _save_inline, text)

    # ── Legacy Obsidian cleanup ──
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    for tag in ["tags:", "date:", "status:", "phase:", "topic:", "aliases:", "cssclasses:"]:
        text = re.sub(rf"^{tag}.*$", "", text, flags=re.MULTILINE)

    # ── Callouts (legacy) → simple text ──
    callout_map = {
        "warning": "!", "tip": "Совет:", "bug": "Баг:", "example": "Пример:",
        "hint": "Подсказка:", "question": "?", "success": "Готово:", "abstract": "Вывод:",
        "info": "Инфо:", "danger": "!", "note": "Заметка:",
    }
    for name, label in callout_map.items():
        text = re.sub(rf">\s*\[!{name}\]\s*(.+)", rf"{label} \1", text, flags=re.IGNORECASE)
        text = re.sub(rf"^\s*\[!{name}\]\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(rf"\[!{name}\]\s*", f"{label} ", text, flags=re.IGNORECASE)

    text = re.sub(r"\[/![^\]]+\]", "", text)
    text = re.sub(r"\[![^\]]*\]", "", text)

    # ── Blockquotes: > text → _text_ ──
    text = re.sub(r"^>\s?(.+)$", r"_\1_", text, flags=re.MULTILINE)

    # ── Headers: # → bold, ## → bold ──
    def _header(m):
        level = len(m.group(1))
        title = m.group(2).strip()
        return f"\n*{title}*\n"
    text = re.sub(r"^(#{1,3})\s+(.+)$", _header, text, flags=re.MULTILINE)

    # ── Horizontal rules ──
    text = re.sub(r"^─+$|^---+$|^─────+\s*$", "────────────────────────", text, flags=re.MULTILINE)

    # ── Tables (legacy) → bullet list ──
    lines = text.split("\n")
    result = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
            if re.match(r"^\|[\s\-:|]+$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            result.append(f"  - {'  '.join(cells)}")
        else:
            if in_table:
                in_table = False
            result.append(line)
    text = "\n".join(result)

    # ── Bold: **text** → *text* ──
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

    # ── Clean whitespace ──
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\n+", "", text)
    text = text.strip()

    # ── Restore code blocks (simple, no frames) ──
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
        return f"\n```\n{code}\n```"

    text = re.sub(r"%%CODE_(\d+)%%", _restore_code, text)

    # ── Restore inline code ──
    def _restore_inline(m):
        return inline_codes[int(m.group(1))]
    text = re.sub(r"%%IC_(\d+)%%", _restore_inline, text)

    # Final cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def split_for_telegram(text: str, max_len: int = 3900) -> list[str]:
    if len(text) <= max_len:
        return [text]

    sections = []
    current = ""
    in_code = False

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
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
