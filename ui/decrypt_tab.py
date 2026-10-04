import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.encryptor import decrypt_file
from core.file_handler import (
    get_file_extension,
    get_file_size_readable,
    validate_file_exists,
)
from database.db_manager import log_operation
from ui import theme


class DecryptTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, **kwargs)
        self._file_path: str | None = None
        self._show_password = False
        self._build()

    def _build(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="فك تشفير ملف",
            font=theme.font_heading(),
            text_color=theme.TEXT_PRIMARY,
        )
        title.pack(anchor="e", padx=20, pady=(20, 8))

        info = ctk.CTkFrame(
            self,
            fg_color="#EEF2FF",
            corner_radius=10,
            border_width=1,
            border_color=theme.PRIMARY_COLOR,
        )
        info.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            info,
            text="يُقبل فقط الملفات المشفرة بامتداد .enc",
            font=theme.font_small(),
            text_color=theme.PRIMARY_COLOR,
        ).pack(anchor="e", padx=12, pady=10)

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

        pwd_lbl = ctk.CTkLabel(
            self,
            text="كلمة المرور",
            font=theme.font_body_bold(),
            text_color=theme.TEXT_PRIMARY,
        )
        pwd_lbl.pack(anchor="e", padx=20, pady=(8, 4))

        pwd_row = ctk.CTkFrame(self, fg_color="transparent")
        pwd_row.pack(fill="x", padx=20)

        self.password_entry = ctk.CTkEntry(
            pwd_row,
            height=theme.INPUT_HEIGHT,
            corner_radius=theme.RADIUS_INPUT,
            show="●",
            placeholder_text="أدخل كلمة المرور...",
            font=theme.font_body(),
        )
        self.password_entry.pack(side="right", fill="x", expand=True, padx=(8, 0))

        self.toggle_btn = ctk.CTkButton(
            pwd_row,
            text="إظهار",
            width=72,
            height=theme.BUTTON_HEIGHT,
            corner_radius=theme.RADIUS_BUTTON,
            fg_color="#EEF2FF",
            text_color=theme.PRIMARY_COLOR,
            hover_color=theme.BORDER_COLOR,
            font=theme.font_small(),
            command=self._toggle_password,
        )
        self.toggle_btn.pack(side="right")

        self.decrypt_btn = ctk.CTkButton(
            self,
            text="فك التشفير",
            height=48,
            corner_radius=12,
            fg_color=theme.PRIMARY_LIGHT,
            hover_color=theme.PRIMARY_COLOR,
            font=theme.font_encrypt_button(),
            command=self._on_decrypt,
        )
        self.decrypt_btn.pack(fill="x", padx=20, pady=(16, 8))

        self.result_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=10)
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=theme.font_body_bold(),
            justify="right",
        )
        self.result_label.pack(anchor="e", padx=12, pady=10)
        self.result_frame.pack_forget()

    def _toggle_password(self) -> None:
        try:
            self._show_password = not self._show_password
            if self._show_password:
                self.password_entry.configure(show="")
                self.toggle_btn.configure(text="إخفاء")
            else:
                self.password_entry.configure(show="●")
                self.toggle_btn.configure(text="إظهار")
        except Exception:
            pass

    def _pick_file(self) -> None:
        try:
            path = filedialog.askopenfilename(
                title="اختر ملفاً مشفراً",
                filetypes=[("ملفات مشفرة", "*.enc"), ("جميع الملفات", "*.*")],
            )
            if not path:
                return
            if not path.lower().endswith(".enc"):
                messagebox.showerror(
                    "خطأ",
                    "هذا الملف غير مشفر. اختر ملفاً بامتداد .enc",
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

    def _on_decrypt(self) -> None:
        try:
            path = self._file_path
            if not path or not validate_file_exists(path):
                messagebox.showerror("خطأ", "يرجى اختيار ملف أولاً")
                return
            if not path.lower().endswith(".enc"):
                messagebox.showerror(
                    "خطأ",
                    "هذا الملف غير مشفر. اختر ملفاً بامتداد .enc",
                )
                return

            pwd = self.password_entry.get().strip()
            if not pwd:
                messagebox.showerror("خطأ", "يرجى إدخال كلمة مرور")
                return

            name = os.path.basename(path)
            size_s = get_file_size_readable(path)
            ext = get_file_extension(path)

            ok, msg = decrypt_file(path, pwd)

            if ok:
                self._show_result(True, "تم فك التشفير بنجاح ✓")
                try:
                    log_operation("فك تشفير", name, size_s, ext, "نجح", None)
                except Exception:
                    pass
            else:
                display = msg
                if msg == "كلمة المرور غير صحيحة":
                    display = "كلمة المرور غير صحيحة — يرجى المحاولة مرة أخرى"
                self._show_result(False, display)
                try:
                    log_operation("فك تشفير", name, size_s, ext, "فشل", msg)
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
