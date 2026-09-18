import mss
import cv2
import json
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

class CalibratorGUI:
    """
    Visual overlay tool to help calibrate screen detection coordinates and HSV color ranges.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GPO Macro Screen Calibrator")
        self.root.geometry("450x380")
        
        with open("config.json", "r") as f:
            self.config = json.load(f)
            
        self.sct = mss.mss()
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(frame, text="Screen Coordinate & Color Calibrator", font=("Helvetica", 12, "bold"))
        lbl.pack(pady=5)

        info = ttk.Label(frame, text="Select region to test color values:", font=("Helvetica", 9))
        info.pack(pady=3)

        self.region_var = tk.StringVar(value="flag_status")
        reg_cb = ttk.Combobox(frame, textvariable=self.region_var, values=list(self.config["regions"].keys()))
        reg_cb.pack(pady=5)

        test_btn = ttk.Button(frame, text="📸 Capture & Test Region", command=self._test_region)
        test_btn.pack(pady=10)

        self.result_lbl = ttk.Label(frame, text="Results: Click capture to test.", font=("Consolas", 9), wraplength=400)
        self.result_lbl.pack(pady=10)

    def _test_region(self):
        reg_name = self.region_var.get()
        if reg_name not in self.config["regions"]:
            return
            
        reg = self.config["regions"][reg_name]
        monitor = {"top": reg["y"], "left": reg["x"], "width": reg["width"], "height": reg["height"]}
        
        try:
            sct_img = self.sct.grab(monitor)
            frame = np.array(sct_img)
            bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            
            mean_hsv = np.mean(hsv, axis=(0,1))
            res_str = f"Region: '{reg_name}' ({reg['width']}x{reg['height']})\n" \
                      f"Average HSV: H={mean_hsv[0]:.1f}, S={mean_hsv[1]:.1f}, V={mean_hsv[2]:.1f}\n" \
                      f"Sample captured successfully!"
            self.result_lbl.config(text=res_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed screen capture: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalibratorGUI(root)
    root.mainloop()
