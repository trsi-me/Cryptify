import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import customtkinter as ctk

from database.db_manager import clear_all_logs, get_all_logs, get_stats
from ui import theme


class HistoryTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color=theme.BACKGROUND, **kwargs)
        self._build()
        self.refresh_data()

    def _build(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(
            top,
            text="سجل العمليات",
            font=theme.font_heading(),
            text_color=theme.TEXT_PRIMARY,
        )
        title.pack(side="left")

        btn_row = ctk.CTkFrame(top, fg_color="transparent")
        btn_row.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_row,
            text="تحديث",
            width=90,
            height=36,
            corner_radius=8,
            fg_color="#EEF2FF",
            text_color=theme.PRIMARY_COLOR,
            hover_color=theme.BORDER_COLOR,
            font=theme.font_small(),
            command=self.refresh_data,
        )
        refresh_btn.pack(side="left", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            btn_row,
            text="مسح الكل",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="#FEF2F2",
            text_color=theme.ERROR_COLOR,
            hover_color=theme.BORDER_COLOR,
            font=theme.font_small(),
            command=self._on_clear_all,
        )
        clear_btn.pack(side="left")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=16, pady=(0, 8))

        self.stat_total = self._stat_box(stats, "إجمالي العمليات:", "0", theme.TEXT_PRIMARY)
        self.stat_ok = self._stat_box(stats, "ناجحة:", "0", theme.SUCCESS_COLOR)
        self.stat_fail = self._stat_box(stats, "فاشلة:", "0", theme.ERROR_COLOR)

        self._table_wrap = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            corner_radius=theme.RADIUS_FRAME,
            border_width=1,
            border_color=theme.BORDER_COLOR,
        )
        self._table_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._table_inner = tk.Frame(self._table_wrap, bg=theme.SURFACE)
        self._table_inner.pack(fill="both", expand=True, padx=4, pady=4)

        self._empty_label = ctk.CTkLabel(
            self._table_wrap,
            text="لا توجد سجلات",
            font=theme.font_body(),
            text_color=theme.TEXT_SECONDARY,
        )

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        fam = theme.get_font(12)[0]
        style.configure(
            "Cryptify.Treeview",
            font=(fam, 12),
            rowheight=26,
            background=theme.SURFACE,
            fieldbackground=theme.SURFACE,
            foreground=theme.TEXT_PRIMARY,
        )
        style.configure(
            "Cryptify.Treeview.Heading",
            font=(fam, 12, "bold"),
            background=theme.PRIMARY_COLOR,
            foreground="white",
            relief="flat",
        )
        style.map(
            "Cryptify.Treeview.Heading",
            background=[("active", theme.PRIMARY_LIGHT)],
        )

        cols = ("id", "operation", "file_name", "file_size", "file_type", "status", "timestamp")
        self.tree = ttk.Treeview(
            self._table_inner,
            columns=cols,
            show="headings",
            style="Cryptify.Treeview",
            selectmode="browse",
        )

        headings = {
            "id": "#",
            "operation": "النوع",
            "file_name": "اسم الملف",
            "file_size": "الحجم",
            "file_type": "الامتداد",
            "status": "الحالة",
            "timestamp": "التاريخ والوقت",
        }
        widths = {
            "id": 40,
            "operation": 100,
            "file_name": 200,
            "file_size": 80,
            "file_type": 70,
            "status": 70,
            "timestamp": 150,
        }

        for c in cols:
            self.tree.heading(c, text=headings[c])
            stretch = c == "file_name"
            self.tree.column(c, width=widths[c], anchor="center", stretch=stretch)

        vsb = ttk.Scrollbar(self._table_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._table_inner.grid_rowconfigure(0, weight=1)
        self._table_inner.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("ok", foreground=theme.SUCCESS_COLOR)
        self.tree.tag_configure("fail", foreground=theme.ERROR_COLOR)

    def _stat_box(self, parent, label: str, value: str, color: str) -> ctk.CTkLabel:
        box = ctk.CTkFrame(
            parent,
            fg_color=theme.SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=theme.BORDER_COLOR,
        )
        box.pack(side="left", padx=(0, 8), fill="x", expand=True)

        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            inner,
            text=label,
            font=theme.font_small(),
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="e")

        val = ctk.CTkLabel(
            inner,
            text=value,
            font=theme.font_body_bold(),
            text_color=color,
        )
        val.pack(anchor="e")
        return val

    def _on_clear_all(self) -> None:
        try:
            ok = messagebox.askyesno(
                "تأكيد",
                "هل أنت متأكد من حذف جميع السجلات؟",
            )
            if not ok:
                return
            clear_all_logs()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def refresh_data(self) -> None:
        try:
            stats = get_stats()
            self.stat_total.configure(text=str(stats["total"]))
            self.stat_ok.configure(text=str(stats["success"]))
            self.stat_fail.configure(text=str(stats["failed"]))

            for item in self.tree.get_children():
                self.tree.delete(item)

            logs = get_all_logs()
            if not logs:
                self._table_inner.pack_forget()
                self._empty_label.pack(expand=True, pady=40)
            else:
                self._empty_label.pack_forget()
                self._table_inner.pack(fill="both", expand=True, padx=4, pady=4)

            for row in logs:
                tag = "ok" if row.get("status") == "نجح" else "fail"
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("id", ""),
                        row.get("operation", ""),
                        row.get("file_name", ""),
                        row.get("file_size", ""),
                        row.get("file_type", ""),
                        row.get("status", ""),
                        row.get("timestamp", ""),
                    ),
                    tags=(tag,),
                )
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تحميل السجل: {e}")
