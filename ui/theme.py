import tkinter as tk
import tkinter.font as tkfont

PRIMARY_COLOR = "#1A3A8F"
PRIMARY_LIGHT = "#2A5FD4"
ACCENT_COLOR = "#00C2CB"
BACKGROUND = "#F5F7FA"
SURFACE = "#FFFFFF"
TEXT_PRIMARY = "#1E2340"
TEXT_SECONDARY = "#6B7280"
BORDER_COLOR = "#E0E4EF"
SUCCESS_COLOR = "#22C55E"
ERROR_COLOR = "#EF4444"
WARNING_COLOR = "#F59E0B"

RADIUS_BUTTON = 10
RADIUS_INPUT = 10
RADIUS_FRAME = 12

BUTTON_HEIGHT = 44
INPUT_HEIGHT = 44

BUTTON_PADX = 20
BUTTON_PADY = 0

_FONT_FAMILY_CACHE: str | None = None


def _resolve_font_family() -> str:
    global _FONT_FAMILY_CACHE
    if _FONT_FAMILY_CACHE is not None:
        return _FONT_FAMILY_CACHE
    try:
        root = tk._default_root
        if root is None:
            root = tk.Tk()
            root.withdraw()
            fams = set(tkfont.families())
            root.destroy()
        else:
            fams = set(tkfont.families())
        _FONT_FAMILY_CACHE = "Cairo" if "Cairo" in fams else "Segoe UI"
    except Exception:
        _FONT_FAMILY_CACHE = "Segoe UI"
    return _FONT_FAMILY_CACHE


def get_font(size: int, weight: str = "normal") -> tuple:
    family = _resolve_font_family()
    if weight == "normal":
        return (family, size)
    return (family, size, weight)


def font_title() -> tuple:
    return get_font(22, "bold")


def font_heading() -> tuple:
    return get_font(16, "bold")


def font_subheading() -> tuple:
    return get_font(14, "bold")


def font_body() -> tuple:
    return get_font(13)


def font_body_bold() -> tuple:
    return get_font(13, "bold")


def font_small() -> tuple:
    return get_font(11)


def font_button() -> tuple:
    return get_font(13, "bold")


def font_tab() -> tuple:
    return get_font(13, "bold")


def font_encrypt_button() -> tuple:
    return get_font(14, "bold")
