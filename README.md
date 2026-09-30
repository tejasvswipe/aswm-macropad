# hackpad:
UltimateEdition Macro pad powered by an ESP32-S3 and a N8R8 main character, featuring 8 mechanical keys, a smooth rotary encoder, 2 OLED displays using an I2C mux, and 11 RGB addressable LEDs, all to bring maximum productivity to your desk!
---## The Setup (Pin Mapping)> No Cap: Make sure to check these pins in KiCad netlists before etching your board!

| Component | What it do | GPIO | Receipts |
| :--- | :--- | :---: | :--- |
| Display Mux | SDA / SCL | `GPIO8` / `GPIO9` | pull-ups are your friends! |
| Neon Lighting | WS2812B Data | `GPIO4` | requires 5V logic shifts |
| The Dial | Encoder A / B / SW | `GPIO5` / `GPIO6` / `GPIO7` | uses quadrature ISR |
| Top Keys | SW1 / SW2 | `GPIO1` / `GPIO2` | crisped debounced |
| Mid Keys | SW3 / SW4 / SW7 | `GPIO42` / `GPIO41` / `GPIO40` | crisped debounced v2 |
| Bot Keys | SW6 / SW8 / SW9 | `GPIO39` / `GPIO38` / `GPIO21` | swap these keys if they do dumb things |
### 🎹 Keymap Layout
┌───────────────┐ ┌───────────────┐

│ [SW1] │ │ [SW2] │ --> Copy/Paste macro pair (real)
│ Ctrl + C │ │ Ctrl + V │
├───────────────┼─┴───────────────┤
│ [SW3] │ [SW4] │ --> Workspace hoppers
│ Win + 1 │ Win + 2 │
├───────────────┼─────────────────┤
│ [SW7] │ [ENC TURN] │ --> Increase volume (2% steps)
│ Win + 3 │ [ENC PUSH] │ --> Toggle Mute button (when mom walks in)
├───────────────┼─────────────────┤
│ [SW6] │ [SW8] │ [SW9] --> Hardcoded spam for
│ tejas.com │ tejas.com │ tejas.com the domain clout
└───────────────┴─────────────────┘

Screen 1 (DS1): Time, date, and visual slider. Clean.
Screen 2 (DS2): Spotify ticker (Title, Artist, and track progress tracker).
---

#### 🚀 The Roadmap (Let Him Cook)

Phase 1 Phase 2 Phase 3 Phase 4 Phase 5
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ USB │ ────> │ Inputs │ ────> │ RGB FX │ ────> │ Screens │ ────> │ Companion│
│ Vibes │ │ Secured │ │ Activated│ │ In Sync │ │ Script │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
-----------------
  Phase 1: Native USB Stack - Implement HID Keyboard + Media Control + CDC Serial. (Files: `src/main.cpp`, `platformio.ini`)
Phase 2: Input Engine - Software debouncing of the keys + High-priority interrupt loop for encoder (so it never misses a step). (Files: `src/main.cpp`, `src/config.h`)
Phase 3: Chroma Lighting - Rainbow cycle when idle, fast white flash on key-press, and low-key red breathing animation when muted. (Files: `src/leds.h`)
Phase 4: Dual-Screen flex - Drive two identical screens (`0x3C`) using a TCA9548A multiplexer. We isolated the drawing code completely to Core 0 to prevent UI lag while playing games. (Files: `src/ui.h`)
Phase 5: Windows Companion Data Syncing - Backend Python script to feed PC metrics and Spotify telemetry to the board over USB. (Files: `host/companion.py`)
---

## ⚡ Host Serial Protocol
Serial data is sent using a simple low-header Tab-Separated Values (`\t`) encoding:

Time: `T \t `
Audio: `V \t  \t `
Spotify: `S \t  \t  \t  \t  \t

Do you want to start writing the C++ code for `src/config.h` to finalize these pins, or would you like to write the Py
thon `companion.py` to start tracking your Spotify streams?