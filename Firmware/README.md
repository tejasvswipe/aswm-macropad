# Hackpad firmware

This is CircuitPython firmware for the **actual PCB in this repository**: a Seeed XIAO RP2040, 4×4 diode matrix, and EC11 encoder.

## Install

1. Install CircuitPython for **Seeed XIAO RP2040**.
2. Copy `boot.py` and `code.py` to the board's `CIRCUITPY` drive.
3. Copy the `adafruit_hid` library folder from the CircuitPython bundle to `CIRCUITPY/lib/`.
4. Reconnect USB. The board now appears as a keyboard plus media-control device.

## Keymap

| Key | Action |
|---|---|
| SW1 | Ctrl+C |
| SW2 | Ctrl+V |
| SW3 | Chrome next tab, Ctrl+Tab |
| SW4 | Chrome previous tab, Ctrl+Shift+Tab |
| SW5 | Chrome new tab, Ctrl+T |
| SW6 | Close tab, Ctrl+W |
| SW7 | Focus address bar, Ctrl+L |
| SW8…SW16 | Win+1…Win+9 |
| Encoder clockwise/counter-clockwise | Volume up/down |
| Encoder press | Play/pause media, including Spotify |

If the encoder direction is backwards, swap `ENC_A` and `ENC_B` in `code.py`.

## Important hardware note

The committed PCB does **not** contain the OLED displays, I²C mux, ESP32-S3, or RGB LEDs described in the README text. It is a 4×4 matrix wired to every usable XIAO RP2040 GPIO. Therefore this firmware cannot display the current time on the shipped PCB without a hardware revision that adds an OLED and frees/reroutes I²C pins.

`host/companion.py` is included as an optional time sender for a future display-equipped revision; it is not needed for the keys or encoder.

