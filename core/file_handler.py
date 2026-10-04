import os
from pathlib import Path


def get_file_size_readable(file_path: str) -> str:
    try:
        size = os.path.getsize(file_path)
    except OSError:
        return "0 B"

    for unit, label in (
        (1024**3, "GB"),
        (1024**2, "MB"),
        (1024, "KB"),
    ):
        if size >= unit:
            return f"{size / unit:.1f} {label}"
    return f"{size} B"


def get_file_extension(file_path: str) -> str:
    try:
        ext = Path(file_path).suffix.lower()
        return ext if ext else "."
    except Exception:
        return "."


def validate_file_exists(file_path: str) -> bool:
    try:
        return Path(file_path).is_file()
    except Exception:
        return False


def get_supported_types() -> list[str]:
    return [
        ".pdf",
        ".docx",
        ".doc",
        ".jpg",
        ".jpeg",
        ".png",
        ".txt",
        ".xlsx",
        ".xls",
        ".enc",
    ]
