"""
Парсинг Markdown-файлов уроков для Telegram.

Конвертирует Obsidian-формат в Telegram Markdown:
  # Header      →  *HEADER*
  > [!tip] ...  →  💡 ...
  ```python     →  content (pre-formatted)
  | a | b |     →  a • b
  [[link]]      →  link
  ---           →  ──────────
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

    # ── Wikilinks: [[text]] → text ──
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # ── Obsidian metadata lines ──
    for tag in ["tags:", "date:", "status:", "phase:", "topic:", "aliases:", "cssclasses:"]:
        text = re.sub(rf"^{tag}.*$", "", text, flags=re.MULTILINE)

    # ── Callouts: > [!name] Title ──
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

    # ── Blockquotes: > text → text ──
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)

    # ── Headers: ## Header → *HEADER* ──
    def _header(m):
        level = len(m.group(1))
        title = m.group(2).strip()
        if level == 1:
            return f"\n*{'━' * 20}*\n*{title.upper()}*\n*{'━' * 20}*"
        return f"\n*{title}*"
    text = re.sub(r"^(#{1,3})\s+(.+)$", _header, text, flags=re.MULTILINE)

    # ── Horizontal rules: --- → ──────── ──
    text = re.sub(r"^─+$|^---+$", "─" * 24, text, flags=re.MULTILINE)
    text = re.sub(r"^─────+\s*$", "─" * 24, text, flags=re.MULTILINE)

    # ── Tables: | a | b | → a • b ──
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
            result.append("  " + "  •  ".join(cells))
        else:
            if in_table:
                in_table = False
            result.append(line)
    text = "\n".join(result)

    # ── Code blocks: keep content, add pre markers ──
    def _code_block(m):
        lang = m.group(1) or ""
        code = m.group(2).strip()
        if lang == "python":
            lines = code.split("\n")
            formatted = []
            for line in lines:
                if "#" in line:
                    code_part, comment = line.split("#", 1)
                    formatted.append(f"{code_part.rstrip()} #{comment}")
                else:
                    formatted.append(line)
            code = "\n".join(formatted)
        return f"\n```\n{code}\n```\n"
    text = re.sub(r"```(\w*)\n(.*?)```", _code_block, text, flags=re.DOTALL)

    # ── Bold: **text** → *text* ──
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)

    # ── Clean excess whitespace ──
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\n+", "", text)
    text = text.strip()

    return text


def split_for_telegram(text: str, max_len: int = 3900) -> list[str]:
    if len(text) <= max_len:
        return [text]

    sections = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len and current.strip():
            sections.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        sections.append(current.strip())

    # Try to merge very short trailing sections
    if len(sections) > 1 and len(sections[-1]) < 500:
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
