"""
Парсинг Markdown-файлов уроков для Telegram.

Конвертирует Obsidian-формат в Telegram Markdown.
Код извлекается ДО обработки — заголовки и ** внутри кода не ломаются.
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

    # ── Extract code blocks first (protect from transformations) ──
    code_blocks = []

    def _save_code(m):
        lang = m.group(1) or ""
        code = m.group(2).strip()
        idx = len(code_blocks)
        code_blocks.append((lang, code))
        return f"\n%%CODEBLOCK_{idx}%%\n"

    text = re.sub(r"```(\w*)\n(.*?)```", _save_code, text, flags=re.DOTALL)

    # ── Now safe to transform text ──

    # Wikilinks: [[text]] → text
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # Obsidian metadata lines
    for tag in ["tags:", "date:", "status:", "phase:", "topic:", "aliases:", "cssclasses:"]:
        text = re.sub(rf"^{tag}.*$", "", text, flags=re.MULTILINE)

    # Callouts: > [!name] Title → emoji Title
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

    # Blockquotes: > text → text
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)

    # Headers → bold with decoration
    def _header(m):
        level = len(m.group(1))
        title = m.group(2).strip()
        if level == 1:
            return f"\n*{title.upper()}*\n{'━' * 28}"
        return f"\n*▸ {title}*"
    text = re.sub(r"^(#{1,3})\s+(.+)$", _header, text, flags=re.MULTILINE)

    # Horizontal rules
    text = re.sub(r"^─+$|^---+$", "·" * 30, text, flags=re.MULTILINE)
    text = re.sub(r"^─────+\s*$", "·" * 30, text, flags=re.MULTILINE)

    # Tables: | a | b | → a • b
    lines = text.split("\n")
    result = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                result.append("")  # blank line before table
            if re.match(r"^\|[\s\-:|]+$", stripped):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            result.append("  " + "  •  ".join(cells))
        else:
            if in_table:
                in_table = False
                result.append("")  # blank line after table
            result.append(line)
    text = "\n".join(result)

    # Bold: **text** → *text* (but not inside `backticks`)
    inline_codes = []
    def _save_inline(m):
        idx = len(inline_codes)
        inline_codes.append(m.group(0))
        return f"%%INLINE_{idx}%%"
    text = re.sub(r"`[^`]+`", _save_inline, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)
    def _restore_inline(m):
        return inline_codes[int(m.group(1))]
    text = re.sub(r"%%INLINE_(\d+)%%", _restore_inline, text)

    # Clean excess whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\n+", "", text)
    text = text.strip()

    # ── Restore code blocks with formatting ──
    def _restore_code(m):
        idx = int(m.group(1))
        lang, code = code_blocks[idx]
        # Format python comments nicely
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

    text = re.sub(r"%%CODEBLOCK_(\d+)%%", _restore_code, text)

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
        if line.strip().startswith("```"):
            in_code = not in_code

        if len(current) + len(line) + 1 > max_len and current.strip() and not in_code:
            sections.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"

    if current.strip():
        sections.append(current.strip())

    # Merge short trailing section
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
