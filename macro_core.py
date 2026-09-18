import time
import subprocess
import threading
import pyautogui
from pynput import keyboard
from vision_detector import VisionDetector

class MacroCore:
    """
    Sett's Arena Infamy Macro Core Finite State Machine.
    Controls macro logic, key presses, state transitions, and server hopping.
    """
    def __init__(self, config: dict, log_callback=None):
        self.config = config
        self.log_cb = log_callback or print
        self.detector = VisionDetector(config)

        self.running = False
        self.paused = False
        self.claims_count = 0

        # Safety configuration
        pyautogui.FAILSAFE = True

        # Emergency stop listener thread
        self.stop_key = config["keybinds"]["emergency_stop"].lower()
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def log(self, msg: str):
        self.log_cb(f"[MACRO] {msg}")

    def _on_key_press(self, key):
        try:
            if hasattr(key, 'name') and key.name.lower() == self.stop_key:
                self.log(f"Emergency Stop key ({self.stop_key.upper()}) pressed! Stopping macro...")
                self.stop()
        except Exception:
            pass

    def start(self):
        """Starts the main macro loop in a background thread."""
        if self.running:
            return
        self.running = True
        self.paused = False
        self.claims_count = 0
        threading.Thread(target=self._run_loop, daemon=True).start()
        self.log("Macro engine started.")

    def stop(self):
        """Stops the macro engine."""
        self.running = False
        self.log("Macro engine stopped.")

    def pause(self):
        """Toggles pause state."""
        self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        self.log(f"Macro {state}.")

    def _run_loop(self):
        """
        Main Macro Loop:
        1. Check if flag is free. If taken -> Server Hop.
        2. Walk to flag & claim it.
        3. Wait in safe zone.
        4. When infamy ready -> Geppo up out of safe zone, then fall back into safety.
        5. Repeat claim up to twice or until flag is taken -> Server Hop.
        6. End loop if death detected.
        """
        self.log("Beginning Sett's Arena Infamy loop...")

        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue

            # Check for death state
            if self.detector.is_player_dead():
                self.log("DEATH DETECTED! Stopping macro loop.")
                self.stop()
                break

            self.log("Step 1: Checking Sett's Arena Flag state...")
            if not self.detector.is_flag_free():
                self.log("Flag is taken or contested. Initiating Server Hop...")
                self._server_hop()
                continue

            self.log("Flag is FREE! Proceeding to claim Sett's Arena Flag...")
            self._claim_flag()

            # Main waiting loop for infamy ticks in current server
            self.claims_count = 0
            while self.running and not self.paused and self.claims_count < 2:
                self.log(f"Waiting in safe zone (Claims: {self.claims_count}/2)...")

                tick_start = time.time()
                infamy_claimed = False

                while self.running and not self.paused:
                    # Check death
                    if self.detector.is_player_dead():
                        self.log("DEATH DETECTED while waiting in safe zone! Stopping macro.")
                        self.stop()
                        return

                    # Check if flag was lost/taken by enemy
                    if self.detector.is_flag_taken():
                        self.log("Flag was TAKEN by an enemy! Breaking wait loop to Server Hop...")
                        break

                    # Check if infamy is ready to claim
                    if self.detector.is_infamy_ready():
                        self.log("Infamy tick READY! Performing Geppo out of safe zone...")
                        self._geppo_tick()
                        self.claims_count += 1
                        infamy_claimed = True
                        break

                    # Fallback timer check based on GPO cooldown settings
                    elapsed = time.time() - tick_start
                    cooldown = self.config["timings"]["infamy_tick_cooldown_sec"]
                    if elapsed >= cooldown + 5:
                        self.log(f"Infamy cooldown elapsed ({cooldown}s). Attempting Geppo tick...")
                        self._geppo_tick()
                        self.claims_count += 1
                        infamy_claimed = True
                        break

                    time.sleep(self.config["timings"]["loop_poll_sec"])

                # If flag was lost, break loop to hop servers
                if not infamy_claimed and self.detector.is_flag_taken():
                    break

            self.log(f"Server sequence completed (Total Claims: {self.claims_count}). Hopping to next server...")
            self._server_hop()

    def _claim_flag(self):
        """Moves player forward and holds interact key to claim Sett's flag."""
        interact_key = self.config["keybinds"]["interact"]
        fwd_key = self.config["keybinds"]["forward"]
        hold_time = self.config["timings"]["claim_hold_sec"]

        # Walk towards flag
        pyautogui.keyDown(fwd_key)
        time.sleep(1.0)
        pyautogui.keyUp(fwd_key)

        # Interact to claim flag
        self.log(f"Holding interact key '{interact_key}' to claim flag...")
        pyautogui.keyDown(interact_key)
        time.sleep(hold_time)
        pyautogui.keyUp(interact_key)

        self.log("Flag claim action complete. Returning to safe zone...")
        # Move back into safety zone
        pyautogui.keyDown("s")
        time.sleep(1.0)
        pyautogui.keyUp("s")

    def _geppo_tick(self):
        """
        Geppos straight up out of the safe zone to trigger the infamy claim tick,
        then falls back down into the safety zone.
        """
        geppo_key = self.config["keybinds"]["geppo"]
        jumps = self.config["timings"]["geppo_jump_count"]
        interval = self.config["timings"]["geppo_interval_sec"]
        fall_delay = self.config["timings"]["geppo_fall_delay_sec"]

        self.log(f"Executing {jumps} Geppo jumps using '{geppo_key}'...")
        for _ in range(jumps):
            pyautogui.press(geppo_key)
            time.sleep(interval)

        self.log(f"Waiting {fall_delay}s to fall back into safe zone...")
        time.sleep(fall_delay)
        self.log("Returned safely to safe zone.")

    def _server_hop(self):
        """
        Executes server hop via deep link or hotkey, then waits for game load.
        """
        method = self.config["server_hop"]["method"]
        wait_sec = self.config["timings"]["server_join_wait_sec"]

        if method == "deep_link":
            url = self.config["server_hop"]["rejoin_url"]
            self.log(f"Launching server hop via deep link: {url}")
            try:
                subprocess.Popen(["open", url]) # macOS URL launcher
            except Exception as e:
                self.log(f"Deep link launch error: {e}")
        else:
            hop_key = self.config["keybinds"]["server_hop_key"]
            self.log(f"Pressing server hop key '{hop_key}'...")
            pyautogui.press(hop_key)

        self.log(f"Waiting {wait_sec} seconds for new server loading screen...")
        time.sleep(wait_sec)
        self.log("Server hop wait finished.")
