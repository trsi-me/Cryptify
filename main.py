import customtkinter as ctk

from database.db_manager import initialize_db
from ui.main_window import MainWindow


def main() -> None:
    try:
        initialize_db()
    except Exception as e:
        raise RuntimeError(f"فشل تهيئة قاعدة البيانات: {e}") from e

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
