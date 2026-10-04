import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.encryptor import encrypt_file
from core.file_handler import (
    get_file_extension,
    get_file_size_readable,
    get_supported_types,
    validate_file_exists,
)
from database.db_manager import log_operation
from ui import theme


def _password_diverse(p: str) -> bool:
    has_lower = any(c.islower() for c in p)
    has_upper = any(c.isupper() for c in p)
    has_digit = any(c.isdigit() for c in p)
    has_sym = any(not c.isalnum() for c in p)
    return sum([has_lower, has_upper, has_digit, has_sym]) >= 3


def _strength_level(password: str) -> tuple[float, str, str]:
    n = len(password)
    if n < 6:
        return 0.25, "ضعيفة", theme.ERROR_COLOR
    if n <= 9:
        return 0.5, "متوسطة", theme.WARNING_COLOR
    if n >= 10 and _password_diverse(password):
        return 1.0, "قوية", theme.SUCCESS_COLOR
    return 0.66, "متوسطة", theme.WARNING_COLOR


class EncryptTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, **kwargs)
        self._file_path: str | None = None
        self._build()

    def _build(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="تشفير ملف",
            font=theme.font_heading(),
            text_color=theme.TEXT_PRIMARY,
        )
        title.pack(anchor="e", padx=20, pady=(20, 8))

        file_frame = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=theme.RADIUS_FRAME,
            border_width=1,
            border_color=theme.BORDER_COLOR,
        )
        file_frame.pack(fill="x", padx=20, pady=(0, 8))

        row = ctk.CTkFrame(file_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=12)

        ctk.CTkLabel(
            row,
            text="الملف المختار:",
            font=theme.font_body_bold(),
            text_color=theme.TEXT_PRIMARY,
        ).pack(side="right", padx=(8, 0))

        self.path_entry = ctk.CTkEntry(
            row,
            height=theme.INPUT_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            state="readonly",
            font=theme.font_body(),
        )
        self.path_entry.pack(side="right", fill="x", expand=True, padx=(8, 0))

        pick = ctk.CTkButton(
            row,
            text="اختيار ملف",
            width=130,
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_LIGHT,
            font=theme.font_button(),
            command=self._pick_file,
        )
        pick.pack(side="right")

        self.info_row = ctk.CTkFrame(self, fg_color="transparent")
        self.size_lbl = ctk.CTkLabel(
            self.info_row,
            text="الحجم: —",
            font=theme.font_small(),
            text_color=theme.TEXT_SECONDARY,
        )
        self.type_lbl = ctk.CTkLabel(
            self.info_row,
            text="النوع: —",
            font=theme.font_small(),
            text_color=theme.TEXT_SECONDARY,
        )
        self.size_lbl.pack(side="right", padx=(16, 0))
        self.type_lbl.pack(side="right")
        self.info_row.pack_forget()

        ctk.CTkLabel(
            self,
            text="كلمة المرور",
            font=theme.font_body_bold(),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="e", padx=20, pady=(8, 4))

        self.password_entry = ctk.CTkEntry(
            self,
            height=theme.INPUT_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            show="●",
            placeholder_text="أدخل كلمة مرور قوية...",
            font=theme.font_body(),
        )
        self.password_entry.pack(fill="x", padx=20)
        self.password_entry.bind("<KeyRelease>", self._on_password_change)

        ctk.CTkLabel(
            self,
            text="تأكيد كلمة المرور",
            font=theme.font_body_bold(),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="e", padx=20, pady=(8, 4))

        self.confirm_entry = ctk.CTkEntry(
            self,
            height=theme.INPUT_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            show="●",
            placeholder_text="أعد إدخال كلمة المرور...",
            font=theme.font_body(),
        )
        self.confirm_entry.pack(fill="x", padx=20)

        strength_row = ctk.CTkFrame(self, fg_color="transparent")
        strength_row.pack(fill="x", padx=20, pady=(10, 4))

        self.strength_bar = ctk.CTkProgressBar(
            strength_row,
            height=10,
            corner_radius=5,
            progress_color=theme.ERROR_COLOR,
        )
        self.strength_bar.pack(side="right", fill="x", expand=True, padx=(8, 0))
        self.strength_bar.set(0.1)

        self.strength_lbl = ctk.CTkLabel(
            strength_row,
            text="ضعيفة",
            font=theme.font_small(),
            text_color=theme.TEXT_SECONDARY,
            width=56,
        )
        self.strength_lbl.pack(side="right")

        self.encrypt_btn = ctk.CTkButton(
            self,
            text="تشفير الملف",
            height=48,
            corner_radius=12,
            fg_color=theme.PRIMARY_COLOR,
            hover_color=theme.PRIMARY_LIGHT,
            font=theme.font_encrypt_button(),
            command=self._on_encrypt,
        )
        self.encrypt_btn.pack(fill="x", padx=20, pady=(12, 8))

        self.result_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=10)
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=theme.font_body_bold(),
            justify="right",
        )
        self.result_label.pack(anchor="e", padx=12, pady=10)
        self.result_frame.pack_forget()

        self._on_password_change()

    def _on_password_change(self, _event=None) -> None:
        try:
            p = self.password_entry.get()
            ratio, label, color = _strength_level(p)
            self.strength_bar.set(ratio)
            self.strength_bar.configure(progress_color=color)
            self.strength_lbl.configure(text=label, text_color=color)
        except Exception:
            pass

    def _pick_file(self) -> None:
        try:
            exts = [e for e in get_supported_types() if e != ".enc"]
            patterns = " ".join(f"*{e}" for e in exts)
            path = filedialog.askopenfilename(
                title="اختر ملفاً للتشفير",
                filetypes=[
                    ("ملفات مدعومة", patterns),
                    ("جميع الملفات", "*.*"),
                ],
            )
            if not path:
                return
            if path.lower().endswith(".enc"):
                messagebox.showerror(
                    "خطأ",
                    "لا يمكن تشفير ملف مشفر. اختر ملفاً غير بامتداد .enc",
                )
                return
            self._file_path = path
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, os.path.basename(path))
            self.path_entry.configure(state="readonly")

            self.size_lbl.configure(text=f"الحجم: {get_file_size_readable(path)}")
            self.type_lbl.configure(text=f"النوع: {get_file_extension(path)}")
            self.info_row.pack(fill="x", padx=20, pady=(0, 8))
            self.result_frame.pack_forget()
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def _on_encrypt(self) -> None:
        try:
            path = self._file_path
            if not path or not validate_file_exists(path):
                self._show_result(False, "يرجى اختيار ملف أولاً")
                return

            pwd = self.password_entry.get()
            confirm = self.confirm_entry.get()

            if not pwd.strip():
                self._show_result(False, "يرجى إدخال كلمة مرور")
                return
            if pwd != confirm:
                self._show_result(False, "كلمتا المرور غير متطابقتين")
                return
            if len(pwd) < 4:
                self._show_result(
                    False,
                    "كلمة المرور قصيرة جداً — الحد الأدنى 4 أحرف",
                )
                return

            name = os.path.basename(path)
            size_s = get_file_size_readable(path)
            ext = get_file_extension(path)

            ok, msg = encrypt_file(path, pwd)

            if ok:
                self._show_result(True, "تم التشفير بنجاح ✓")
                try:
                    log_operation("تشفير", name, size_s, ext, "نجح", None)
                except Exception:
                    pass
            else:
                self._show_result(False, msg)
                try:
                    log_operation("تشفير", name, size_s, ext, "فشل", msg)
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def _show_result(self, success: bool, text: str) -> None:
        try:
            if success:
                self.result_frame.configure(
                    fg_color="#F0FDF4",
                    border_width=1,
                    border_color=theme.SUCCESS_COLOR,
                )
                self.result_label.configure(text=text, text_color=theme.SUCCESS_COLOR)
            else:
                self.result_frame.configure(
                    fg_color="#FEF2F2",
                    border_width=1,
                    border_color=theme.ERROR_COLOR,
                )
                self.result_label.configure(text=text, text_color=theme.ERROR_COLOR)
            self.result_frame.pack(fill="x", padx=20, pady=(8, 12))
        except Exception:
            pass
