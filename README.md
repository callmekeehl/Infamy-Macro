# GPO Sett's Arena Infamy Macro (No Injection)

An external, pixel/vision-based macro for Grand Piece Online (GPO) on Roblox designed specifically for automating infamy farming at **Sett's Arena**.

## 🛡️ Safety & Architecture
- **No Memory Injection**: Operates 100% externally via screen capture (`mss`/`OpenCV`) and synthetic input simulation (`pyautogui`/`pynput`).
- **Does not edit or read Roblox game memory or process handles.**
- Includes **Emergency Stop (Hotkey: F6)** and PyAutoGUI failsafe (moving cursor to screen corner instantly halts execution).

---

## 🚀 Features & Automation Flow
1. **Flag Availability Scan**: Inspects Sett's Arena flag region. If free, proceeds to claim. If taken or contested, automatically hops servers.
2. **Flag Claiming**: Walks into the flag circle and holds interact key (`E`).
3. **Safe Zone Idling**: Returns to safety zone and monitors for claim readiness.
4. **Geppo Claim Tick**: When infamy is ready to claim, performs Geppo jumps (`Space`) straight up out of the safety zone to collect the infamy tick, then falls back down safely.
5. **Multi-Claim & Rejoin Loop**: Repeats claim up to **2 times** per server, or immediately server hops if the flag is lost/taken.
6. **Death Detection**: Monitors health status and stops immediately if player death occurs.

---

## 📦 How to Run (No Coding Required!)

### macOS:
Double-click [`run_macro.command`](file:///Users/justkeehl/IdeaProjects/GPO%20Infamy%20MACRO/run_macro.command) in Finder.

### Windows:
Double-click [`run_macro.bat`](file:///Users/justkeehl/IdeaProjects/GPO%20Infamy%20MACRO/run_macro.bat) in File Explorer.

*The script will automatically check/install requirements and launch the GUI launcher!*

---

## ⚙️ Configuration (`config.json`)
You can tweak settings directly inside the **GUI Settings tab** or edit `config.json`:
- `keybinds`: Custom key mapping for interact, geppo, movement, and hotkeys.
- `timings`: Delays for server loading, flag hold time, Geppo jump counts, and infamy tick intervals.
- `regions`: Screen bounding boxes for flag status, infamy indicators, and health bar.
