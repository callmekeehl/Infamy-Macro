import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from macro_core import MacroStateMachine

class MacroGUI:
    """
    Tkinter Desktop GUI for configuring, calibrating, and running the GPO Infamy Macro.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GPO Sett's Arena Infamy Macro (No Injection)")
        self.root.geometry("620x520")
        self.root.resizable(False, False)

        # Load config
        self.config_path = "config.json"
        self.config = self._load_config()

        # Macro engine instance
        self.macro = MacroStateMachine(self.config, log_callback=self.log_message)

        # Build UI layout
        self._build_ui()


    def _load_config(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception:
            messagebox.showerror("Error", "Could not load config.json! Please verify file exists.")
            return {}

    def _save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def log_message(self, message: str):
        """Thread-safe UI logging."""
        def append():
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
        self.root.after(0, append)

    def _build_ui(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="GPO Sett's Arena Infamy Macro", font=("Helvetica", 14, "bold"))
        title_lbl.pack(anchor=tk.W)
        sub_lbl = ttk.Label(header_frame, text="External Screen-Vision Macro • Safe No Injection Engine", font=("Helvetica", 9, "italic"))
        sub_lbl.pack(anchor=tk.W)

        # Notebook Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Control Panel
        tab_control = ttk.Frame(notebook, padding=10)
        notebook.add(tab_control, text="Control Panel")

        ctrl_btn_frame = ttk.Frame(tab_control)
        ctrl_btn_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(ctrl_btn_frame, text="▶ Start Macro", command=self._start_macro)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(ctrl_btn_frame, text="⏸ Pause / Resume", command=self._pause_macro)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(ctrl_btn_frame, text="⏹ Stop Macro", command=self._stop_macro)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        info_lbl = ttk.Label(tab_control, text="Emergency Stop Hotkey: F6  |  Failsafe: Drag mouse to screen corner", font=("Helvetica", 9))
        info_lbl.pack(anchor=tk.W, pady=5)

        # Live Log Display
        log_frame = ttk.LabelFrame(tab_control, text="Live Log & Status", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=14, font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Settings & Keybinds
        tab_settings = ttk.Frame(notebook, padding=10)
        notebook.add(tab_settings, text="Keybinds & Settings")

        # Keybind entries
        keys_frame = ttk.LabelFrame(tab_settings, text="Keybind Configuration", padding=10)
        keys_frame.pack(fill=tk.X, pady=5)

        self.key_entries = {}
        for idx, (k, v) in enumerate(self.config.get("keybinds", {}).items()):
            row = idx // 2
            col = (idx % 2) * 2

            lbl = ttk.Label(keys_frame, text=f"{k.capitalize()}:")
            lbl.grid(row=row, column=col, sticky=tk.W, padx=5, pady=3)

            ent = ttk.Entry(keys_frame, width=10)
            ent.insert(0, str(v))
            ent.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=3)
            self.key_entries[k] = ent

        # Timings entries
        time_frame = ttk.LabelFrame(tab_settings, text="Timing Delays (seconds)", padding=10)
        time_frame.pack(fill=tk.X, pady=5)

        self.time_entries = {}
        for idx, (k, v) in enumerate(self.config.get("timings", {}).items()):
            row = idx // 2
            col = (idx % 2) * 2

            lbl = ttk.Label(time_frame, text=f"{k.replace('_', ' ').title()}:")
            lbl.grid(row=row, column=col, sticky=tk.W, padx=5, pady=3)

            ent = ttk.Entry(time_frame, width=10)
            ent.insert(0, str(v))
            ent.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=3)
            self.time_entries[k] = ent

        # Hop method frame
        hop_frame = ttk.LabelFrame(tab_settings, text="Server Hop Method", padding=10)
        hop_frame.pack(fill=tk.X, pady=5)

        self.hop_method_var = tk.StringVar(value=self.config.get("server_hop", {}).get("method", "in_game_ui"))
        r1 = ttk.Radiobutton(hop_frame, text="In-Game UI Menu Clicks (Recommended)", variable=self.hop_method_var, value="in_game_ui")
        r1.pack(anchor=tk.W)
        r2 = ttk.Radiobutton(hop_frame, text="Deep Link / Roblox Protocol Rejoin", variable=self.hop_method_var, value="deep_link")
        r2.pack(anchor=tk.W)

        save_btn = ttk.Button(tab_settings, text="💾 Save Settings", command=self._apply_settings)
        save_btn.pack(anchor=tk.E, pady=10)


    def _start_macro(self):
        self.macro.start()

    def _pause_macro(self):
        self.macro.pause()

    def _stop_macro(self):
        self.macro.stop()

    def _apply_settings(self):
        # Update config dictionary from UI entries
        for k, ent in self.key_entries.items():
            self.config["keybinds"][k] = ent.get()

        for k, ent in self.time_entries.items():
            try:
                val = float(ent.get())
                self.config["timings"][k] = val if "." in ent.get() else int(val)
            except ValueError:
                pass

        if "server_hop" not in self.config:
            self.config["server_hop"] = {}
        self.config["server_hop"]["method"] = self.hop_method_var.get()

        self._save_config()
        self.macro.config = self.config


if __name__ == "__main__":
    root = tk.Tk()
    app = MacroGUI(root)
    root.mainloop()
