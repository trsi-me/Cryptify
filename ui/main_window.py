from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ui.decrypt_tab import DecryptTab
from ui.encrypt_tab import EncryptTab
from ui.history_tab import HistoryTab
from ui import theme
from utils.helpers import resource_path


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Cryptify — نظام تشفير الملفات")
        self.geometry("900x620")
        self.resizable(False, False)
        self.configure(fg_color=theme.BACKGROUND)
        self._center_on_screen(900, 620)
        self._build_header()
        self._build_tabs()

    def _center_on_screen(self, w: int, h: int) -> None:
        try:
            self.update_idletasks()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=70, fg_color=theme.PRIMARY_COLOR, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=10)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left")

        logo_path = resource_path("assets", "images", "Logo.png")
        try:
            if Path(logo_path).is_file():
                pil_img = Image.open(logo_path)
                self._logo_ctk = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(40, 40),
                )
                logo_lbl = ctk.CTkLabel(left, image=self._logo_ctk, text="")
                logo_lbl.pack(side="left", padx=(0, 10))
        except Exception:
            self._logo_ctk = None

        ctk.CTkLabel(
            left,
            text="Cryptify",
            font=theme.get_font(18, "bold"),
            text_color="white",
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text="نظام تشفير الملفات",
            font=theme.font_small(),
            text_color="#E8EDFF",
        ).pack(side="right")

    def _build_tabs(self) -> None:
        try:
            self.tabview = ctk.CTkTabview(
                self,
                fg_color=theme.BACKGROUND,
                segmented_button_fg_color=theme.BORDER_COLOR,
                segmented_button_selected_color=theme.PRIMARY_COLOR,
                segmented_button_selected_hover_color=theme.PRIMARY_LIGHT,
                segmented_button_unselected_color=theme.BACKGROUND,
                segmented_button_unselected_hover_color=theme.SURFACE,
                text_color=theme.TEXT_SECONDARY,
                corner_radius=8,
            )
            self.tabview.pack(fill="both", expand=True, padx=12, pady=(0, 12))

            tab_enc = self.tabview.add("تشفير الملف")
            tab_dec = self.tabview.add("فك التشفير")
            tab_hist = self.tabview.add("سجل العمليات")

            enc = EncryptTab(tab_enc)
            enc.pack(fill="both", expand=True)

            dec = DecryptTab(tab_dec)
            dec.pack(fill="both", expand=True)

            hist = HistoryTab(tab_hist)
            hist.pack(fill="both", expand=True)
        except Exception:
            raise
