"""
Хранение данных пользователей в SQLite.

Таблицы:
  users        — прогресс, streak, закладки, настройки напоминаний
  quiz_results — результаты тестов по урокам

Используй get_user_progress() для чтения, update_user_progress() для записи.
Потокобезопасно: sqlite3 + WAL mode.
"""
import sqlite3
import json
from datetime import datetime, timedelta

from .config import DB_FILE

_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _init_db(_conn)
    return _conn


def _init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            current     INTEGER DEFAULT 0,
            completed   TEXT DEFAULT '[]',
            bookmarks   TEXT DEFAULT '[]',
            streak      INTEGER DEFAULT 0,
            last_active TEXT,
            started     TEXT,
            reminder_h  INTEGER DEFAULT 8,
            reminder_m  INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS quiz_results (
            user_id     INTEGER,
            lesson_idx  INTEGER,
            score       INTEGER,
            total       INTEGER,
            completed_at TEXT,
            PRIMARY KEY (user_id, lesson_idx)
        );
    """)


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "current": row["current"],
        "completed": json.loads(row["completed"]),
        "bookmarks": json.loads(row["bookmarks"]),
        "streak": row["streak"],
        "last_active": row["last_active"],
        "started": row["started"],
        "reminder_h": row["reminder_h"],
        "reminder_m": row["reminder_m"],
    }


def get_user_progress(user_id: int) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO users (user_id, started) VALUES (?, ?)",
            (user_id, now),
        )
        conn.commit()
        return {
            "current": 0, "completed": [], "bookmarks": [],
            "streak": 0, "last_active": None, "started": now,
            "reminder_h": 8, "reminder_m": 0,
        }
    return _row_to_dict(row)


def update_user_progress(user_id: int, lesson_idx: int, completed: bool = False):
    conn = _get_conn()
    p = get_user_progress(user_id)
    if completed and lesson_idx not in p["completed"]:
        p["completed"].append(lesson_idx)
    conn.execute(
        "UPDATE users SET current = ?, completed = ? WHERE user_id = ?",
        (lesson_idx, json.dumps(p["completed"]), user_id),
    )
    conn.commit()
    _update_streak(user_id)


def _update_streak(user_id: int):
    conn = _get_conn()
    row = conn.execute("SELECT streak, last_active FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    last = row["last_active"]
    if last == today:
        return
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
    if last == yesterday:
        streak = row["streak"] + 1
    else:
        streak = 1
    conn.execute(
        "UPDATE users SET streak = ?, last_active = ? WHERE user_id = ?",
        (streak, today, user_id),
    )
    conn.commit()


def toggle_bookmark(user_id: int, lesson_idx: int) -> str:
    conn = _get_conn()
    p = get_user_progress(user_id)
    bms = p["bookmarks"]
    if lesson_idx in bms:
        bms.remove(lesson_idx)
        msg = "❌ Убрано из закладок"
    else:
        bms.append(lesson_idx)
        msg = "✅ Добавлено в закладки"
    conn.execute(
        "UPDATE users SET bookmarks = ? WHERE user_id = ?",
        (json.dumps(bms), user_id),
    )
    conn.commit()
    return msg


def reset_user(user_id: int):
    conn = _get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE users SET current = 0, completed = '[]', bookmarks = '[]', "
        "streak = 0, last_active = NULL, started = ? WHERE user_id = ?",
        (now, user_id),
    )
    conn.commit()


def set_reminder(user_id: int, hour: int, minute: int):
    conn = _get_conn()
    conn.execute(
        "UPDATE users SET reminder_h = ?, reminder_m = ? WHERE user_id = ?",
        (hour, minute, user_id),
    )
    conn.commit()


def get_all_users() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM users").fetchall()
    return [{"user_id": row["user_id"], **_row_to_dict(row)} for row in rows]


def save_quiz_result(user_id: int, lesson_idx: int, score: int, total: int):
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO quiz_results (user_id, lesson_idx, score, total, completed_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, lesson_idx, score, total, datetime.now().isoformat()),
    )
    conn.commit()


def get_quiz_result(user_id: int, lesson_idx: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM quiz_results WHERE user_id = ? AND lesson_idx = ?",
        (user_id, lesson_idx),
    ).fetchone()
    if row:
        return {"score": row["score"], "total": row["total"], "completed_at": row["completed_at"]}
    return None
