import time
import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button

class InputController:
    """
    OS-level direct keypress and mouse input controller using pynput & pyautogui.
    Manages safe key release and input sequences without memory injection.
    """
    def __init__(self, config: dict):
        self.config = config
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def release_all_keys(self):
        """Emergency release of all movement, interact, and jump keys."""
        keys_to_release = ['w', 'a', 's', 'd', 'e', 'q', Key.space, Key.shift]
        for k in keys_to_release:
            try:
                self.keyboard.release(k)
            except Exception:
                pass
        try:
            pyautogui.keyUp('w')
            pyautogui.keyUp('s')
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')
            pyautogui.keyUp('e')
            pyautogui.keyUp('space')
        except Exception:
            pass

    def click_at(self, x: int, y: int, delay: float = 0.5):
        """Simulates native OS mouse click at given screen coordinate."""
        pyautogui.click(x, y)
        time.sleep(delay)

    def press_key(self, key_str: str, duration: float = 0.1):
        """Presses and releases a single key."""
        pyautogui.press(key_str)
        time.sleep(duration)

    def hold_key(self, key_str: str, duration: float):
        """Holds down a specified key for a duration in seconds."""
        pyautogui.keyDown(key_str)
        time.sleep(duration)
        pyautogui.keyUp(key_str)

    def geppo_sequence(self, jumps: int = 3, interval: float = 0.2):
        """Executes a series of Geppo sky-walk jumps."""
        geppo_key = self.config["keybinds"]["geppo"]
        for _ in range(jumps):
            pyautogui.press(geppo_key)
            time.sleep(interval)
