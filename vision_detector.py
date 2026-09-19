import mss
import numpy as np
import cv2
from typing import Dict, Tuple, List, Optional

class ScreenScanner:
    """
    High-performance desktop frame scanning engine built on mss & OpenCV.
    Operates strictly externally on screen pixels without touching process memory.
    """
    def __init__(self, config: dict):
        self.config = config
        self.sct = mss.mss()

    def capture_screen_region(self, monitor_dict: dict) -> np.ndarray:
        """
        Captures a specific screen bounding box defined by pixel coordinates.
        Returns BGR numpy image array.
        """
        sct_img = self.sct.grab(monitor_dict)
        frame = np.array(sct_img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def capture_named_region(self, region_key: str, screen_size: Tuple[int, int]) -> np.ndarray:
        """
        Captures a region named in config, dynamically converting ratios to pixels if needed.
        """
        reg = self.config["regions"][region_key]
        sw, sh = screen_size

        if "x_ratio" in reg:
            top = int(sh * reg["y_ratio"])
            left = int(sw * reg["x_ratio"])
            width = int(sw * reg["w_ratio"])
            height = int(sh * reg["h_ratio"])
        else:
            top = reg["y"]
            left = reg["x"]
            width = reg["width"]
            height = reg["height"]

        monitor = {"top": top, "left": left, "width": width, "height": height}
        return self.capture_screen_region(monitor)

    def is_death_detected(self, screen_size: Tuple[int, int]) -> bool:
        """
        Continuous health bar / death overlay visual scanner.
        Returns True if health bar is zeroed out or red respawn filter is present.
        """
        try:
            img = self.capture_named_region("health_bar", screen_size)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)

            thresh = self.config["color_targets"]["death_black_threshold"]
            return avg_brightness < thresh
        except Exception:
            return False

    def check_server_crew_flag_icon(self, server_row_img: np.ndarray) -> bool:
        """
        Scans a server row image for the specific Crew Flag Icon.
        If missing, server lacks required crew population for flag mechanics.
        """
        try:
            hsv = cv2.cvtColor(server_row_img, cv2.COLOR_BGR2HSV)
            low = np.array(self.config["color_targets"]["flag_icon_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["flag_icon_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            match_pixels = cv2.countNonZero(mask)

            # Threshold for crew flag icon presence
            return match_pixels > 25
        except Exception:
            return False

    def is_flag_free(self, screen_size: Tuple[int, int]) -> bool:
        """
        Scans Sett's Flag HUD state to check if flag is Free / Neutral.
        """
        try:
            img = self.capture_named_region("flag_status_hud", screen_size)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["flag_free_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["flag_free_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            return cv2.countNonZero(mask) > 40
        except Exception:
            return False

    def is_flag_taken(self, screen_size: Tuple[int, int]) -> bool:
        """
        Scans Sett's Flag HUD state to check if flag was captured by rival players.
        """
        try:
            img = self.capture_named_region("flag_status_hud", screen_size)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["flag_taken_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["flag_taken_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            return cv2.countNonZero(mask) > 40
        except Exception:
            return False

    def is_infamy_ready(self, screen_size: Tuple[int, int]) -> bool:
        """
        Scans HUD element indicating Infamy drop is ready to harvest.
        """
        try:
            img = self.capture_named_region("infamy_ready_hud", screen_size)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["infamy_ready_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["infamy_ready_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            return cv2.countNonZero(mask) > 25
        except Exception:
            return False
