import time
import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController

class InputEngine:
    """
    Direct OS-level input engine (keyboard & mouse simulation).
    Handles key movement, Geppo sky-walk jumps, zoom scrolls, and clicking configurable zones.
    """
    def __init__(self, config: dict):
        self.config = config
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        pyautogui.FAILSAFE = True

    def release_all_keys(self):
        """Releases all held movement and action keys."""
        for k in ['w', 'a', 's', 'd', 'space', Key.space, Key.shift]:
            try:
                self.keyboard.release(k)
            except Exception:
                pass
        for k in ['w', 's', 'a', 'd', 'space']:
            try:
                pyautogui.keyUp(k)
            except Exception:
                pass

    def click_zone_center(self, zone_key: str, delay_after: float = 0.8):
        """Clicks the exact center of a configured zone."""
        z = self.config["zones"][zone_key]
        cx = int(z["x"] + z["w"] / 2)
        cy = int(z["y"] + z["h"] / 2)
        pyautogui.click(cx, cy)
        time.sleep(delay_after)

    def zoom_out(self, ticks: int = 6):
        """Scrolls down to zoom camera out for a broader view of the flag."""
        pyautogui.scroll(-ticks)
        time.sleep(0.5)

    def walk_forward(self, seconds: float):
        """Holds 'W' to walk forward into flag capture circle."""
        fwd_key = self.config["keybinds"]["forward"]
        pyautogui.keyDown(fwd_key)
        time.sleep(seconds)
        pyautogui.keyUp(fwd_key)

    def retreat_backward(self, seconds: float):
        """Holds 'S' to walk backward into safe zone."""
        back_key = self.config["keybinds"]["backward"]
        pyautogui.keyDown(back_key)
        time.sleep(seconds)
        pyautogui.keyUp(back_key)

    def geppo_skywalk(self, jumps: int = 4, interval: float = 0.2):
        """Executes Geppo sky-walk jumps straight up out of safe zone."""
        geppo_key = self.config["keybinds"]["geppo"]
        for _ in range(jumps):
            pyautogui.press(geppo_key)
            time.sleep(interval)
