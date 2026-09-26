import mss
import numpy as np
import cv2
from typing import Dict, Tuple

class VisionEngine:
    """
    Sub-10ms frame grabber and visual analysis engine using mss and OpenCV.
    Operates strictly externally on screen pixels without process memory access.
    """
    def __init__(self, config: dict):
        self.config = config
        self.sct = mss.mss()

    def capture_zone(self, zone_key: str) -> np.ndarray:
        """
        Captures pixels for a specified zone from config.json.
        Returns BGR numpy image array.
        """
        z = self.config["zones"][zone_key]
        monitor = {
            "top": max(0, int(z["y"])),
            "left": max(0, int(z["x"])),
            "width": max(1, int(z["w"])),
            "height": max(1, int(z["h"]))
        }
        sct_img = self.sct.grab(monitor)
        frame = np.array(sct_img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def is_hp_zero(self) -> bool:
        """
        Analyzes the red HP Bar Zone. Returns True if HP bar brightness drops below threshold (HP = 0).
        """
        try:
            img = self.capture_zone("hp_bar_zone")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            return avg_brightness < 25.0
        except Exception:
            return False

    def is_flag_100_percent(self) -> bool:
        """
        Analyzes the Cyan Flag Capture % Text Zone to check if flag capture is 100% complete.
        Checks for bright white/green text pixel concentration indicating claim completion.
        """
        try:
            img = self.capture_zone("flag_capture_pct_text")
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # White/Light Green text filter
            low_val = np.array([0, 0, 180], dtype=np.uint8)
            high_val = np.array([180, 80, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, low_val, high_val)
            
            match_pixels = cv2.countNonZero(mask)
            return match_pixels > 35
        except Exception:
            return False

    def is_flag_taken_by_enemy(self) -> bool:
        """
        Scans the Whole Flag Area (Green Zone) for rival/red ownership indicators.
        """
        try:
            img = self.capture_zone("whole_flag_area")
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Red color range for enemy claimed flag
            low_red1 = np.array([0, 120, 120], dtype=np.uint8)
            high_red1 = np.array([10, 255, 255], dtype=np.uint8)
            low_red2 = np.array([170, 120, 120], dtype=np.uint8)
            high_red2 = np.array([180, 255, 255], dtype=np.uint8)
            
            m1 = cv2.inRange(hsv, low_red1, high_red1)
            m2 = cv2.inRange(hsv, low_red2, high_red2)
            total_red = cv2.countNonZero(m1) + cv2.countNonZero(m2)
            
            return total_red > 60
        except Exception:
            return False
