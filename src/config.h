#pragma once
#include <Arduino.h>
// =====================================================================
//  PIN MAP  -  !!! VERIFY EVERY NUMBER HERE AGAINST YOUR KICAD NETS !!!
//  (I could not trace wires from the schematic image.)
//  Avoid: 0,3,45,46 (strapping), 19,20 (USB D-/D+), 26-32 (flash),
//  33-37 (octal PSRAM on N8R8 modules).
// =====================================================================

// --- I2C + mux (TCA9548A, A0/A1/A2 = GND -> 0x70) ---
#define PIN_SDA        8
#define PIN_SCL        9
#define PIN_TCA_RESET  -1      // -1 = RESET pin tied to 3V3 on the PCB
#define TCA_ADDR       0x70
#define OLED_ADDR      0x3C
#define TCA_CH_INFO    0       // DS1 : time + volume
#define TCA_CH_SPOTIFY 1       // DS2 : Spotify mini player

// --- WS2812B chain (data enters at D13) ---
// Chain order: D13,D14,D15,D16,D17,D18,D12,D10,D9,D8,D7
#define PIN_LED_DATA   4
#define LED_COUNT      11
#define LED_BRIGHTNESS 60      // 0-255

// --- Rotary encoder (EC11) ---
#define PIN_ENC_A      5
#define PIN_ENC_B      6
#define PIN_ENC_SW     7       // S2 -> mute
#define ENC_TRANSITIONS_PER_DETENT 4   // 4 for most EC11, 2 for some
#define ENC_INVERT     false   // flip if volume goes the wrong way
#define VOLUME_STEP    2       // Windows changes 2% per media key

// --- Switches (active-low to GND, internal pull-ups) ---
#define PIN_SW1        1       // top-left  : Copy
#define PIN_SW2        2       // Paste
#define PIN_SW3        42      // Win+1
#define PIN_SW4        41      // Win+2
#define PIN_SW7        40      // Win+3
#define PIN_SW6        39      // bottom row (unassigned)
#define PIN_SW8        38      // bottom row (unassigned)
#define PIN_SW9        21      // bottom row (unassigned)

// LED index (position in chain) nearest each key - tweak to taste
#define LED_SW1 1
#define LED_SW2 2
#define LED_SW3 3
#define LED_SW4 4
#define LED_SW7 5
#define LED_SW9 9
#define LED_SW6 8
#define LED_SW8 7

#define DEBOUNCE_MS      6
#define UNASSIGNED_TEXT  "tejas.com"
#define HOST_TIMEOUT_MS  5000
