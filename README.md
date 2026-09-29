#  hackpad: 
Ultimate EditionThis macro pad goes *so* hard. Powered by an ESP32-S3 with that **N8R8 main character energy**, it packs 8 mechanical keys, a silky rotary encoder, dual OLEDs running through an I2C mux, and 11 addressable RGB LEDs to maximize your desk aesthetics. It’s giving peak productivity. 
---##  The Setup (Pin Mapping)>  **No Cap:** Go verify these pins in your KiCad netlists before you cook your board. 

| Component | What it do | GPIO | Receipts |
| :--- | :--- | :---: | :--- |
| **Display Mux** | SDA / SCL | `GPIO8` / `GPIO9` | Needs pull-ups, don't ghost them |
| **Neon Lighting** | WS2812B Data | `GPIO4` | 5V logic shifts required |
| **The Dial** | Encoder A / B / SW | `GPIO5` / `GPIO6` / `GPIO7` | Quadrature ISR enabled |
| **Top Keys** | SW1 / SW2 | `GPIO1` / `GPIO2` | Crispy debouncing |
| **Mid Keys** | SW3 / SW4 / SW7 | `GPIO42` / `GPIO41` / `GPIO40` | Crispy debouncing v2 |
| **Bot Keys** | SW6 / SW8 / SW9 | `GPIO39` / `GPIO38` / `GPIO21` | Swap 'em if they act goofy |
### 🎹 Keymap Layout

┌───────────────┐ ┌───────────────┐
│ [SW1] │ │ [SW2] │ --> Copy/Paste macro duo (real)
│ Ctrl + C │ │ Ctrl + V │
├───────────────┼─┴───────────────┤
│ [SW3] │ [SW4] │ --> Workspace hoppers
│ Win + 1 │ Win + 2 │
├───────────────┼─────────────────┤
│ [SW7] │ [ENC TURN] │ --> Crank the volume (2% steps)
│ Win + 3 │ [ENC PUSH] │ --> Hit the Mute button when mom walks in
├───────────────┼─────────────────┤
│ [SW6] │ [SW8] │ [SW9] --> Hardcoded spam for
│ tejas.com │ tejas.com │ tejas.com the domain clout
└───────────────┴─────────────────┘


* **Screen 1 (DS1):** Time, date, and a visual volume slider. Clean.
* **Screen 2 (DS2):** Spotify ticker (Title, Artist, and live track progress tracker).

---

## 🚀 The Roadmap (Let Him Cook)


Phase 1 Phase 2 Phase 3 Phase 4 Phase 5
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ USB │ ────> │ Inputs │ ────> │ RGB FX │ ────> │ Screens │ ────> │ Companion│
│ Vibes │ │ Secured │ │ Activated│ │ In Sync │ │ Script │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘


* **Phase 1: Native USB Stack** — Setting up HID Keyboard + Media Control + CDC Serial. (Files: `src/main.cpp`, `platformio.ini`)
* **Phase 2: Input Engine** — Software debouncing for the keys and a high-priority interrupt loop for the encoder so it never skips a beat. (Files: `src/main.cpp`, `src/config.h`)
* **Phase 3: Chroma Lighting** — Rainbow cycle when chillin', instant white flash on keypress, and a low-key red breathing animation when you're muted. (Files: `src/leds.h`)
* **Phase 4: Dual-Screen flexing** — Driving two identical screens (`0x3C`) using a TCA9548A multiplexer. We isolated the drawing code entirely to **Core 0** so the UI never stutters while you're gaming. (Files: `src/ui.h`)
* **Phase 5: Windows Companion Data Sync** — A backend Python script feeding PC metrics and Spotify telemetry straight to the board via USB. (Files: `host/companion.py`)

---

## ⚡ Host Serial Protocol
Data streams down the serial pipeline using a super clean, low-overhead Tab-Separated Values (`\t`) syntax:

* **Time:** `T \t <local epoch>`
* **Audio:** `V \t <volume_int> \t <mute_bool>`
* **Spotify:** `S \t <is_playing> \t <position_ms> \t <duration_ms> \t <track_title> \t <artist_name>

## 📦 How to Boot Up

### Flashing the Code
1. Fire up **VS Code** with the **PlatformIO** extension.
2. Hold the hardware **BOOT** button, tap **RESET**, then let go of **BOOT** to enter flash mode.
3. Mash the **Upload** arrow on the bottom taskbar.

### Running the Host Link
Open your terminal, grab the python packages, and launch the companion daemon to start feeding live telemetry to the pad:
```bash
cd host
pip install -r requirements.txt
python companion.py
```


<FollowUp>
Should we start cooking the actual C++ code for **`src/config.h`** to lock in those pins, or do you want to script the Python **`companion.py`** to start tracking your Spotify streams?
</FollowUp>


