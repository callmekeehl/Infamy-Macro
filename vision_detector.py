import mss
import numpy as np
import cv2
from typing import Dict, Tuple

class VisionDetector:
    """
    Visual detection engine using screen capture and color analysis.
    Operates strictly externally on screen pixels without touching game memory.
    """
    def __init__(self, config: dict):
        self.config = config
        self.sct = mss.mss()

    def capture_region(self, region_key: str) -> np.ndarray:
        """
        Captures a region of the screen defined in config.
        Returns BGR numpy image array.
        """
        reg = self.config["regions"][region_key]
        monitor = {
            "top": reg["y"],
            "left": reg["x"],
            "width": reg["width"],
            "height": reg["height"]
        }
        sct_img = self.sct.grab(monitor)
        # Convert BGRA to BGR numpy array
        frame = np.array(sct_img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def is_flag_free(self) -> bool:
        """
        Analyzes Sett's flag status region to check if it's free to claim.
        Returns True if flag free color signature is detected, False otherwise.
        """
        try:
            img = self.capture_region("flag_status")
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["flag_free_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["flag_free_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            match_pixels = cv2.countNonZero(mask)

            # Threshold for detecting flag free indicator
            return match_pixels > 50
        except Exception:
            return False

    def is_flag_taken(self) -> bool:
        """
        Checks if the flag has been taken by an enemy player.
        """
        try:
            img = self.capture_region("flag_status")
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["flag_taken_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["flag_taken_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            match_pixels = cv2.countNonZero(mask)

            return match_pixels > 50
        except Exception:
            return False

    def is_infamy_ready(self) -> bool:
        """
        Detects if Sett's flag infamy is ready to be claimed / ticked.
        """
        try:
            img = self.capture_region("infamy_ready")
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            low = np.array(self.config["color_targets"]["infamy_ready_hsv_low"], dtype=np.uint8)
            high = np.array(self.config["color_targets"]["infamy_ready_hsv_high"], dtype=np.uint8)

            mask = cv2.inRange(hsv, low, high)
            match_pixels = cv2.countNonZero(mask)

            return match_pixels > 30
        except Exception:
            return False

    def is_player_dead(self) -> bool:
        """
        Checks if the player died by analyzing health bar region or screen dark overlay.
        """
        try:
            img = self.capture_region("health_bar")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)

            thresh = self.config["color_targets"]["death_black_threshold"]
            # If health bar is completely dark / zeroed out
            return avg_brightness < thresh
        except Exception:
            return False
