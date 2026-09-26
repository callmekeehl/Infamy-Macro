import time
import threading
from pynput import keyboard
from vision_engine import VisionEngine
from input_engine import InputEngine

class MacroEngine:
    """
    Finite State Machine driving the GPO Sett's Arena Infamy Macro (v2.0).
    Features:
    - F1 global hotkey toggle start/stop.
    - Configurable startup countdown delay.
    - Camera zoom-out for optimal flag visibility.
    - Fresh spawn walk straight to flag zone.
    - Monitor 100% flag capture percentage completion (Cyan Zone).
    - Retreat to Safe Zone.
    - 11-Minute Infamy Geppo harvest loop.
    - Continuous 60 FPS HP Zero monitor (Red Zone) and Flag Stolen check (Green Zone) triggering Server Hop.
    """
    def __init__(self, config: dict, log_cb=None):
        self.config = config
        self.log_cb = log_cb or print

        self.vision = VisionEngine(config)
        self.inputs = InputEngine(config)

        self.running = False
        self.claims_count = 0

        # Global hotkey listener
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()

    def log(self, message: str):
        self.log_cb(f"[MACRO] {message}")

    def _on_key_press(self, key):
        try:
            hk = self.config["keybinds"]["toggle_macro"].lower()
            if hasattr(key, 'name') and key.name.lower() == hk:
                self.toggle_macro()
            elif hasattr(key, 'vk') and key == keyboard.Key.f1:
                self.toggle_macro()
        except Exception:
            pass

    def toggle_macro(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if self.running:
            return
        self.running = True
        self.claims_count = 0
        threading.Thread(target=self._run_state_machine, daemon=True).start()
        self.log("Macro engine launched! Initializing state machine...")

    def stop(self):
        self.running = False
        self.inputs.release_all_keys()
        self.log("Macro engine stopped. All keys released.")

    def _run_state_machine(self):
        # Startup countdown delay
        delay_sec = self.config["timings"].get("startup_delay_sec", 3.0)
        self.log(f"Starting in {delay_sec} seconds... Get ready!")
        for i in range(int(delay_sec), 0, -1):
            if not self.running:
                return
            self.log(f"Countdown: {i}...")
            time.sleep(1.0)

        # Camera Zoom Out
        self.log("Zooming camera out for full arena visibility...")
        self.inputs.zoom_out(self.config["timings"].get("zoom_scroll_ticks", 6))

        while self.running:
            # Check HP Zero
            if self.vision.is_hp_zero():
                self.log("🔴 HP HIT 0 (DEATH DETECTED)! Initiating Server Hop...")
                self._server_hop()
                continue

            # STEP 1: Walk to Flag Zone (From fresh Sett's spawn)
            self.log("Step 1: Walking straight forward to Sett's Flag capture circle...")
            walk_sec = self.config["timings"]["walk_to_flag_sec"]
            self.inputs.walk_forward(walk_sec)

            # STEP 2: Monitor Flag Capture Percentage Completion (Cyan Zone)
            self.log("Step 2: Monitoring Flag Capture % text completion...")
            cap_start = time.time()
            flag_captured = False

            while self.running:
                if self.vision.is_hp_zero():
                    self.log("🔴 HP HIT 0 while capturing flag! Server Hopping...")
                    self._server_hop()
                    break

                if self.vision.is_flag_100_percent():
                    self.log("🩵 Flag Capture reached 100%! Step 2 complete.")
                    flag_captured = True
                    break

                # Timeout fallback (30 seconds)
                if time.time() - cap_start > 30.0:
                    self.log("Flag capture timeout reached. Proceeding to safe zone...")
                    flag_captured = True
                    break

                time.sleep(0.5)

            if not self.running or not flag_captured:
                continue

            # STEP 3: Retreat to Safe Zone
            self.log("Step 3: Retreating backward into Sett's Arena Safe Zone...")
            retreat_sec = self.config["timings"]["retreat_to_safe_sec"]
            self.inputs.retreat_backward(retreat_sec)

            # STEP 4: 11-Minute Infamy Geppo Harvest Loop
            self.claims_count = 0
            while self.running and self.claims_count < 2:
                cycle_min = self.config["timings"].get("infamy_cycle_min", 11.0)
                cycle_sec = cycle_min * 60.0
                self.log(f"Step 4: Idling in Safe Zone. Next Infamy Geppo in {cycle_min} minutes (Claim {self.claims_count+1}/2)...")

                wait_start = time.time()
                while self.running:
                    # Check HP Zero
                    if self.vision.is_hp_zero():
                        self.log("🔴 HP HIT 0 while in safe zone! Server Hopping...")
                        break

                    # Check Flag Stolen / Taken by enemy
                    if self.vision.is_flag_taken_by_enemy():
                        self.log("🟢 Flag stolen by enemy player! Breaking safe zone idle to Server Hop...")
                        break

                    # Check 11-minute timer completion
                    elapsed = time.time() - wait_start
                    if elapsed >= cycle_sec:
                        self.log("✨ 11 Minutes Elapsed! Executing Geppo sky-walk claim out of safe zone...")
                        self._execute_geppo_claim()
                        self.claims_count += 1
                        break

                    time.sleep(1.0)

                # If loop was broken by HP or Flag stolen before 11 mins
                if time.time() - wait_start < cycle_sec:
                    break

            self.log(f"Server session completed ({self.claims_count} claims). Initiating Server Hop...")
            self._server_hop()

    def _execute_geppo_claim(self):
        jumps = self.config["timings"]["geppo_jump_count"]
        interval = self.config["timings"]["geppo_interval_sec"]
        fall_delay = self.config["timings"]["geppo_fall_delay_sec"]

        self.inputs.geppo_skywalk(jumps, interval)
        time.sleep(fall_delay)
        self.log("Returned safely into Sett's Arena Safe Zone.")

    def _server_hop(self):
        delay = self.config["timings"]["ui_click_delay_sec"]
        wait_sec = self.config["timings"]["server_join_wait_sec"]

        self.log("Clicking Top-Left Menu Icon (Blue Zone)...")
        self.inputs.click_zone_center("top_left_menu_icon", delay)

        self.log("Clicking Sub-Menu Server Icon (Yellow Zone)...")
        self.inputs.click_zone_center("sub_menu_server_icon", delay * 1.5)

        self.log("Clicking Server Join Button (Purple Zone)...")
        self.inputs.click_zone_center("server_join_button", delay)

        self.log(f"Waiting {wait_sec} seconds for server loading screen...")
        time.sleep(wait_sec)
        self.log("Server hop complete.")
