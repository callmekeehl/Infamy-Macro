import json
import tkinter as tk
from tkinter import ttk, messagebox
import mss
import numpy as np
import cv2
from PIL import Image, ImageTk

class ZoneSelectorOverlay:
    """
    Interactive full-screen overlay tool that allows users to select, move,
    and resize rectangular zones for each color-coded target with precision.
    """
    def __init__(self, parent, config: dict, save_callback):
        self.parent = parent
        self.config = config
        self.save_cb = save_callback

        self.overlay = tk.Toplevel(parent)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.85)

        self.canvas = tk.Canvas(self.overlay, cursor="cross", bg="gray15", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.selected_zone_key = list(self.config["zones"].keys())[0]
        self.rect_handles = {}

        # Drag state
        self.drag_mode = None  # 'create', 'move', 'resize'
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.active_handle = None

        self._build_controls_bar()
        self._bind_events()
        self.redraw_canvas()

    def _build_controls_bar(self):
        bar = tk.Frame(self.overlay, bg="#1E1E1E", bd=2, relief=tk.RAISED)
        bar.place(relx=0.5, rely=0.04, anchor=tk.N)

        lbl = tk.Label(bar, text="Target Zone:", fg="white", bg="#1E1E1E", font=("Helvetica", 11, "bold"))
        lbl.pack(side=tk.LEFT, padx=8, pady=5)

        zone_options = [f"{z['name']}" for k, z in self.config["zones"].items()]
        self.zone_var = tk.StringVar(value=zone_options[0])

        cb = ttk.Combobox(bar, textvariable=self.zone_var, values=zone_options, state="readonly", width=32)
        cb.pack(side=tk.LEFT, padx=8, pady=5)
        cb.bind("<<ComboboxSelected>>", self._on_zone_select)

        help_lbl = tk.Label(bar, text="[Drag to Draw/Move | Grab handles to Resize]", fg="#00E5FF", bg="#1E1E1E", font=("Helvetica", 9, "italic"))
        help_lbl.pack(side=tk.LEFT, padx=10, pady=5)

        save_btn = tk.Button(bar, text="💾 Save Zones", bg="#00E676", fg="black", font=("Helvetica", 10, "bold"), command=self._save_and_close)
        save_btn.pack(side=tk.LEFT, padx=8, pady=5)

        close_btn = tk.Button(bar, text="❌ Close", bg="#FF1744", fg="white", font=("Helvetica", 10, "bold"), command=self.overlay.destroy)
        close_btn.pack(side=tk.LEFT, padx=8, pady=5)

    def _on_zone_select(self, event=None):
        selected_name = self.zone_var.get()
        for k, z in self.config["zones"].items():
            if z["name"] == selected_name:
                self.selected_zone_key = k
                break
        self.redraw_canvas()

    def _bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

    def redraw_canvas(self):
        self.canvas.delete("all")

        for key, z in self.config["zones"].items():
            x, y, w, h = int(z["x"]), int(z["y"]), int(z["w"]), int(z["h"])
            color = z["color"]
            is_active = (key == self.selected_zone_key)

            line_w = 4 if is_active else 2
            dash = () if is_active else (4, 4)

            # Draw zone rectangle
            rect_id = self.canvas.create_rectangle(x, y, x + w, y + h, outline=color, width=line_w, dash=dash)
            
            # Label
            self.canvas.create_text(x + 5, y - 10, text=z["name"], fill=color, anchor=tk.SW, font=("Helvetica", 10, "bold"))

            # Draw resize handle if active zone
            if is_active:
                # Bottom-right handle
                self.canvas.create_rectangle(x + w - 6, y + h - 6, x + w + 6, y + h + 6, fill=color, outline="white", tags="handle_br")

    def _on_button_press(self, event):
        x, y = event.x, event.y
        z = self.config["zones"][self.selected_zone_key]
        zx, zy, zw, zh = int(z["x"]), int(z["y"]), int(z["w"]), int(z["h"])

        # Check if clicking bottom-right handle for resizing
        if (zx + zw - 8 <= x <= zx + zw + 8) and (zy + zh - 8 <= y <= zy + zh + 8):
            self.drag_mode = 'resize'
        # Check if clicking inside active rectangle for moving
        elif (zx <= x <= zx + zw) and (zy <= y <= zy + zh):
            self.drag_mode = 'move'
            self.drag_start_x = x - zx
            self.drag_start_y = y - zy
        # Otherwise drag to draw new box
        else:
            self.drag_mode = 'create'
            self.drag_start_x = x
            self.drag_start_y = y
            z["x"], z["y"], z["w"], z["h"] = x, y, 10, 10

    def _on_mouse_drag(self, event):
        x, y = event.x, event.y
        z = self.config["zones"][self.selected_zone_key]

        if self.drag_mode == 'create':
            w = max(10, x - self.drag_start_x)
            h = max(10, y - self.drag_start_y)
            z["x"] = self.drag_start_x
            z["y"] = self.drag_start_y
            z["w"] = w
            z["h"] = h
        elif self.drag_mode == 'move':
            z["x"] = max(0, x - self.drag_start_x)
            z["y"] = max(0, y - self.drag_start_y)
        elif self.drag_mode == 'resize':
            z["w"] = max(10, x - int(z["x"]))
            z["h"] = max(10, y - int(z["y"]))

        self.redraw_canvas()

    def _on_button_release(self, event):
        self.drag_mode = None

    def _save_and_close(self):
        self.save_cb(self.config)
        messagebox.showinfo("Success", "All custom multi-color zones saved successfully!")
        self.overlay.destroy()
