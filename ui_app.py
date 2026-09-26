import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk

from macro_engine import MacroEngine
from zone_selector import ZoneSelectorOverlay

# Configure customtkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernMacroGUI(ctk.CTk):
    """
    Modern desktop GUI featuring Light/Dark mode toggle, interactive multi-colored zone selector launcher,
    keybind and timing adjustments, and live status logging.
    """
    def __init__(self):
        super().__init__()

        self.title("GPO Sett's Arena Infamy Macro (v2.0 - No Injection)")
        self.geometry("700x600")
        self.resizable(False, False)

        self.config_path = "config.json"
        self.config = self._load_config()

        # Apply saved theme
        saved_theme = self.config.get("theme", "dark")
        ctk.set_appearance_mode(saved_theme.capitalize())

        # Initialize Macro Engine
        self.macro = MacroEngine(self.config, log_cb=self.log_message)

        # Build UI layout
        self._build_ui()

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception:
            messagebox.showerror("Error", "Could not load config.json!")
            return {}

    def _save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            self.macro.config = self.config
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving config: {e}")

    def log_message(self, message: str):
        def append():
            self.log_textbox.insert(tk.END, message + "\n")
            self.log_textbox.see(tk.END)
        self.after(0, append)

    def _build_ui(self):
        # Header Frame
        header = ctk.CTkFrame(self, corner_radius=10)
        header.pack(fill="x", padx=15, pady=10)

        title_lbl = ctk.CTkLabel(header, text="GPO Sett's Arena Infamy Macro v2.0", font=("Helvetica", 18, "bold"))
        title_lbl.pack(side="left", padx=15, pady=10)

        # Light / Dark Theme Switch
        self.theme_switch = ctk.CTkSwitch(header, text="Dark Mode", command=self._toggle_theme)
        if self.config.get("theme", "dark") == "dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        self.theme_switch.pack(side="right", padx=15, pady=10)

        # Tabview Controls & Settings
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=15, pady=5)

        tab_ctrl = tabview.add("Control Panel")
        tab_zones = tabview.add("Multi-Color Zone Setter")
        tab_settings = tabview.add("Settings & Keybinds")

        # TAB 1: CONTROL PANEL
        btn_row = ctk.CTkFrame(tab_ctrl, fg_color="transparent")
        btn_row.pack(fill="x", pady=10)

        self.start_btn = ctk.CTkButton(btn_row, text="▶ Start (F1)", fg_color="#00E676", text_color="black", hover_color="#00C853", font=("Helvetica", 13, "bold"), command=self.macro.start)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(btn_row, text="⏹ Stop (F1)", fg_color="#FF1744", text_color="white", hover_color="#D50000", font=("Helvetica", 13, "bold"), command=self.macro.stop)
        self.stop_btn.pack(side="left", padx=10)

        hotkey_lbl = ctk.CTkLabel(tab_ctrl, text="💡 Global Hotkey: Press 'F1' anywhere to Start / Stop macro instantly.", font=("Helvetica", 11, "italic"))
        hotkey_lbl.pack(anchor="w", padx=10, pady=5)

        # Log Textbox
        log_frame = ctk.CTkFrame(tab_ctrl, corner_radius=8)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_textbox = scrolledtext.ScrolledText(log_frame, bg="#121212", fg="#00E5FF", font=("Consolas", 10), insertbackground="white")
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=5)

        # TAB 2: MULTI-COLOR ZONE SETTER
        zone_info = ctk.CTkLabel(tab_zones, text="Click below to open the full-screen visual zone editor.\nYou can drag, select, and resize bounding boxes for each colored target zone.", font=("Helvetica", 12))
        zone_info.pack(pady=15)

        open_zone_btn = ctk.CTkButton(tab_zones, text="🎨 Open Interactive Multi-Color Zone Setter", fg_color="#00E5FF", text_color="black", hover_color="#00B8D4", font=("Helvetica", 14, "bold"), command=self._open_zone_editor)
        open_zone_btn.pack(pady=10)

        # Zone Legend Display
        legend_frame = ctk.CTkFrame(tab_zones)
        legend_frame.pack(fill="both", expand=True, padx=15, pady=10)

        for k, z in self.config["zones"].items():
            row = ctk.CTkFrame(legend_frame, fg_color="transparent")
            row.pack(fill="x", pady=3, padx=10)

            dot = ctk.CTkLabel(row, text="█", text_color=z["color"], font=("Helvetica", 14, "bold"))
            dot.pack(side="left", padx=5)

            lbl = ctk.CTkLabel(row, text=f"{z['name']} - ({z['x']}, {z['y']}, {z['w']}x{z['h']})", font=("Helvetica", 11))
            lbl.pack(side="left", padx=5)

        # TAB 3: SETTINGS & KEYBINDS
        settings_scroll = ctk.CTkScrollableFrame(tab_settings)
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Timings
        ctk.CTkLabel(settings_scroll, text="Timings & Delays", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=5)

        self.time_entries = {}
        for k, v in self.config["timings"].items():
            r = ctk.CTkFrame(settings_scroll, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{k.replace('_', ' ').title()}:", width=200, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(r, width=100)
            ent.insert(0, str(v))
            ent.pack(side="left")
            self.time_entries[k] = ent

        save_btn = ctk.CTkButton(settings_scroll, text="💾 Save Settings", fg_color="#00E676", text_color="black", command=self._save_settings_from_tab)
        save_btn.pack(anchor="e", pady=15)

    def _toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
            self.config["theme"] = "dark"
        else:
            ctk.set_appearance_mode("Light")
            self.config["theme"] = "light"
        self._save_config()

    def _open_zone_editor(self):
        ZoneSelectorOverlay(self, self.config, self._on_zones_updated)

    def _on_zones_updated(self, updated_config):
        self.config = updated_config
        self._save_config()

    def _save_settings_from_tab(self):
        for k, ent in self.time_entries.items():
            try:
                val = float(ent.get())
                self.config["timings"][k] = val if "." in ent.get() else int(val)
            except ValueError:
                pass
        self._save_config()
        messagebox.showinfo("Success", "Settings updated!")

if __name__ == "__main__":
    app = ModernMacroGUI()
    app.mainloop()
