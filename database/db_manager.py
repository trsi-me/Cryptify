import sqlite3
from pathlib import Path
from typing import Any, Optional

_BASE_DIR = Path(__file__).resolve().parent
DB_PATH = _BASE_DIR / "cryptify.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    try:
        _BASE_DIR.mkdir(parents=True, exist_ok=True)
        with _get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS operations_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation   TEXT NOT NULL,
                    file_name   TEXT NOT NULL,
                    file_size   TEXT NOT NULL,
                    file_type   TEXT NOT NULL,
                    status      TEXT NOT NULL,
                    error_msg   TEXT,
                    timestamp   TEXT NOT NULL
                )
                """
            )
            conn.commit()
    except sqlite3.Error:
        raise


def log_operation(
    operation: str,
    file_name: str,
    file_size: str,
    file_type: str,
    status: str,
    error_msg: Optional[str] = None,
) -> None:
    try:
        from datetime import datetime

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO operations_log
                (operation, file_name, file_size, file_type, status, error_msg, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (operation, file_name, file_size, file_type, status, error_msg, ts),
            )
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"فشل تسجيل العملية: {e}") from e


def get_all_logs() -> list[dict[str, Any]]:
    try:
        with _get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, operation, file_name, file_size, file_type, status, error_msg, timestamp
                FROM operations_log
                ORDER BY id DESC
                """
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise RuntimeError(f"فشل قراءة السجل: {e}") from e


def clear_all_logs() -> None:
    try:
        with _get_connection() as conn:
            conn.execute("DELETE FROM operations_log")
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"فشل مسح السجل: {e}") from e


def get_stats() -> dict[str, int]:
    try:
        with _get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM operations_log"
            ).fetchone()[0]
            ok = conn.execute(
                "SELECT COUNT(*) FROM operations_log WHERE status = ?",
                ("نجح",),
            ).fetchone()[0]
            fail = conn.execute(
                "SELECT COUNT(*) FROM operations_log WHERE status = ?",
                ("فشل",),
            ).fetchone()[0]
        return {"total": total, "success": ok, "failed": fail}
    except sqlite3.Error as e:
        raise RuntimeError(f"فشل قراءة الإحصائيات: {e}") from e
