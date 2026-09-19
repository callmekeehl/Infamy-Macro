import time
import threading
import pyautogui
from pynput import keyboard
from vision_detector import ScreenScanner
from input_controller import InputController

class MacroStateMachine:
    """
    Production-ready, thread-safe Sett's Arena Infamy Macro State Machine.
    Follows explicit blueprint:
    1. Dedicated 60 FPS Death Monitor thread.
    2. Crew Requirement verification in server list.
    3. In-Server Flag Availability Check.
    4. Initial Flag Claim & Safe Zone Retreat.
    5. Infamy Harvest Loop (Max 2 claims, continuous death & flag loss monitoring).
    """
    def __init__(self, config: dict, log_callback=None):
        self.config = config
        self.log_cb = log_callback or print

        self.scanner = ScreenScanner(config)
        self.inputs = InputController(config)

        self.running = False
        self.paused = False
        self.is_dead = False
        self.claims_count = 0

        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()

        # Emergency stop listener
        self.stop_key = config["keybinds"]["emergency_stop"].lower()
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def log(self, msg: str):
        self.log_cb(f"[MACRO] {msg}")

    def _on_key_press(self, key):
        try:
            if hasattr(key, 'name') and key.name.lower() == self.stop_key:
                self.log(f"Emergency Stop hotkey ({self.stop_key.upper()}) pressed!")
                self.stop()
        except Exception:
            pass

    def start(self):
        """Launches death monitor thread and main macro state machine."""
        if self.running:
            return
        self.running = True
        self.paused = False
        self.is_dead = False
        self.claims_count = 0

        # 1. Global Thread-Safe Death Monitor (Continuous Execution)
        threading.Thread(target=self._death_monitor_loop, daemon=True).start()
        # 2. Main Macro Logic State Machine
        threading.Thread(target=self._run_state_machine, daemon=True).start()
        self.log("Macro state machine & 60 FPS Death Monitor started.")

    def stop(self):
        """Stops macro execution and releases all keys."""
        self.running = False
        self.inputs.release_all_keys()
        self.log("Macro engine stopped. All held keys released.")

    def pause(self):
        self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        self.log(f"Macro {state}.")

    def _death_monitor_loop(self):
        """
        Dedicated thread continuously scanning HUD region for death indicators at ~60 FPS.
        If death detected: instantly sets IS_DEAD=True, releases keys, and halts macro.
        """
        target_fps = self.config["timings"].get("death_monitor_fps", 60)
        interval = 1.0 / target_fps

        while self.running:
            if not self.paused and self.scanner.is_death_detected((self.screen_w, self.screen_h)):
                self.log("💥 DEATH DETECTED BY 60 FPS MONITOR! Releasing all keys & halting...")
                self.is_dead = True
                self.inputs.release_all_keys()
                self.stop()
                break
            time.sleep(interval)

    def _run_state_machine(self):
        """Main FSM executing step-by-step logic."""
        while self.running:
            if self.paused or self.is_dead:
                time.sleep(0.5)
                continue

            # STEP 2: Server Selection & Crew Requirement Verification
            self.log("Step 2: Opening GPO Server List & checking Crew Flag Icon...")
            if not self._server_selection_step():
                continue

            if self.is_dead or not self.running:
                break

            # STEP 3: In-Server Flag Availability Check
            self.log("Step 3: Checking Sett's Arena Flag status in-server...")
            if not self.scanner.is_flag_free((self.screen_w, self.screen_h)):
                self.log("Flag is OCCUPIED / TAKEN by rival players! Disconnecting & hopping...")
                self._disconnect_and_rejoin()
                continue

            # STEP 4: Initial Flag Claim & Safe Zone Retreat
            self.log("Step 4: Flag is FREE! Moving to claim Sett's Flag & retreating to safe zone...")
            self._claim_flag_and_retreat()

            if self.is_dead or not self.running:
                break

            # STEP 5: Infamy Harvest Loop (Max 2 Claims)
            self.log("Step 5: Entering Infamy Harvest Loop (Max 2 claims)...")
            self._infamy_harvest_loop()

            if self.is_dead or not self.running:
                break

            # Reset / disconnect after completing 2 claims or flag loss
            self.log("Sequence complete for server. Leaving server & starting next loop...")
            self._disconnect_and_rejoin()

    def _server_selection_step(self) -> bool:
        """
        Opens GPO Server list and verifies crew flag icon requirement before clicking JOIN.
        """
        targets = self.config.get("ui_click_targets", {})
        delay = self.config["timings"].get("ui_click_delay_sec", 0.8)

        # Click settings icon to open menu
        set_t = targets.get("top_right_settings_btn", {"x_ratio": 0.177, "y_ratio": 0.038})
        self.inputs.click_at(int(self.screen_w * set_t["x_ratio"]), int(self.screen_h * set_t["y_ratio"]), delay)

        # Click server icon to open server browser
        srv_t = targets.get("sub_menu_server_icon", {"x_ratio": 0.115, "y_ratio": 0.038})
        self.inputs.click_at(int(self.screen_w * srv_t["x_ratio"]), int(self.screen_h * srv_t["y_ratio"]), delay * 1.5)

        # Capture server list window region
        server_window_img = self.scanner.capture_named_region("server_list_window", (self.screen_w, self.screen_h))

        # Check for Crew Flag Icon presence
        if self.config["server_hop"].get("require_crew_flag_icon", True):
            has_flag_icon = self.scanner.check_server_crew_flag_icon(server_window_img)
            if not has_flag_icon:
                self.log("⚠️ Server row lacks Crew Flag Icon (under minimum crew population). Skipping server...")
                # Scroll or close server browser to check next
                pyautogui.scroll(-5)
                time.sleep(0.5)
                return False

        # Click JOIN on eligible server
        join_x = int(self.screen_w * 0.730)
        join_y = int(self.screen_h * 0.388)
        self.inputs.click_at(join_x, join_y, delay)

        # Poll screen for world render loading screen timeout
        wait_sec = self.config["timings"]["server_join_wait_sec"]
        self.log(f"Waiting {wait_sec}s for world render...")
        time.sleep(wait_sec)
        return True

    def _claim_flag_and_retreat(self):
        """Simulates movement into flag circle, holds E to claim, and retreats to safe zone."""
        fwd_key = self.config["keybinds"]["forward"]
        back_key = self.config["keybinds"]["backward"]
        interact_key = self.config["keybinds"]["interact"]
        hold_time = self.config["timings"]["claim_hold_sec"]

        # Move forward into flag capture circle
        self.inputs.hold_key(fwd_key, 1.2)

        # Hold interact key to claim flag
        self.log(f"Holding interact key '{interact_key}' to claim flag...")
        self.inputs.hold_key(interact_key, hold_time)

        # Retreat into safe zone
        self.log("Flag claimed! Retreating into Sett's Arena Safe Zone...")
        self.inputs.hold_key(back_key, 1.2)

    def _infamy_harvest_loop(self):
        """
        Continuous polling loop evaluating:
        a. Death Check (handled continuously by death thread)
        b. Flag Loss Check
        c. Infamy Timer Check -> Geppo jump out of safe zone, interact, fall back in.
        """
        self.claims_count = 0

        while self.running and not self.paused and not self.is_dead and self.claims_count < 2:
            self.log(f"Waiting in safe zone for Infamy drop (Claims: {self.claims_count}/2)...")
            tick_start = time.time()
            infamy_harvested = False

            while self.running and not self.paused and not self.is_dead:
                # b. Flag Loss Check
                if self.scanner.is_flag_taken((self.screen_w, self.screen_h)):
                    self.log("⚠️ Flag captured by rival player! Breaking harvest loop...")
                    return

                # c. Infamy Timer Check
                if self.scanner.is_infamy_ready((self.screen_w, self.screen_h)):
                    self.log("✨ Infamy drop READY! Geppo jumping out of safe zone...")
                    self._harvest_infamy_drop()
                    self.claims_count += 1
                    infamy_harvested = True
                    break

                # Cooldown fallback timeout
                cooldown = self.config["timings"]["infamy_tick_cooldown_sec"]
                if time.time() - tick_start >= cooldown + 5:
                    self.log(f"Infamy cooldown ({cooldown}s) elapsed. Executing harvest Geppo...")
                    self._harvest_infamy_drop()
                    self.claims_count += 1
                    infamy_harvested = True
                    break

                time.sleep(self.config["timings"]["loop_poll_sec"])

            if not infamy_harvested:
                break

    def _harvest_infamy_drop(self):
        """Geppo jump sequence upward out of safe zone threshold, interact, and fall back."""
        jumps = self.config["timings"]["geppo_jump_count"]
        interval = self.config["timings"]["geppo_interval_sec"]
        fall_delay = self.config["timings"]["geppo_fall_delay_sec"]
        interact_key = self.config["keybinds"]["interact"]

        # 1. Trigger Geppo jump sequence upward
        self.inputs.geppo_sequence(jumps, interval)

        # 2. Send interact key to harvest infamy drop
        self.inputs.press_key(interact_key)

        # 3. Allow gravity to drop avatar back into safe zone
        time.sleep(fall_delay)
        self.log("Harvest complete. Returned safely into safe zone.")

    def _disconnect_and_rejoin(self):
        """Re-opens menu and initiates server hop."""
        targets = self.config.get("ui_click_targets", {})
        delay = self.config["timings"].get("ui_click_delay_sec", 0.8)

        set_t = targets.get("top_right_settings_btn", {"x_ratio": 0.177, "y_ratio": 0.038})
        self.inputs.click_at(int(self.screen_w * set_t["x_ratio"]), int(self.screen_h * set_t["y_ratio"]), delay)
