#pragma once
#include <Arduino.h>
// =====================================================================
//  PIN MAP - traced from hackpadSCH.pdf (vector data), GPIO number = IOxx label.
//  Confidence: HIGH  keys, encoder, LED data, SCL
//              MEDIUM SDA (IO9), SW7 (IO16) - see README section 5
//  WARNING: IO37 (encoder B) is used by octal PSRAM on N8R8 modules.
//  Use an ESP32-S3-WROOM-1-N8 / N16 / N4R2 module, or move encoder B.
// =====================================================================

// --- I2C + mux (TCA9548A, A0/A1/A2 = GND -> 0x70) ---
#define PIN_SDA        9
#define PIN_SCL        8
#define PIN_TCA_RESET  -1      // -1 = RESET pin tied to 3V3 on the PCB
#define TCA_ADDR       0x70
#define OLED_ADDR      0x3C
#define TCA_CH_INFO    0       // DS1 : time + volume
#define TCA_CH_SPOTIFY 1       // DS2 : Spotify mini player

// --- WS2812B chain (data enters at D13) ---
// Chain order (ASSUMED, starts at D7): D7,D8,D9,D10,D12,D18,D17,D16,D15,D14,D13
// Build with -DLED_WALK_TEST to light one pixel at a time and fix the LED_SWx indices below.
#define PIN_LED_DATA   4       // -> D7 DIN
#define LED_COUNT      11
#define LED_BRIGHTNESS 60      // 0-255

// --- Rotary encoder (EC11) ---
#define PIN_ENC_A      38
#define PIN_ENC_B      37
#define PIN_ENC_SW     41      // S2 -> mute
#define ENC_TRANSITIONS_PER_DETENT 4   // 4 for most EC11, 2 for some
#define ENC_INVERT     false   // flip if volume goes the wrong way
#define VOLUME_STEP    2       // Windows changes 2% per media key

// --- Switches (active-low to GND, internal pull-ups) ---
#define PIN_SW1        6       // top-left  : Copy
#define PIN_SW2        10      // Paste
#define PIN_SW3        7       // Win+1
#define PIN_SW4        5       // Win+2
#define PIN_SW7        16      // Win+3
#define PIN_SW6        2       // bottom row (unassigned)
#define PIN_SW8        1       // bottom row (unassigned)
#define PIN_SW9        3       // bottom row (unassigned)

// LED index (position in chain) nearest each key - tweak to taste
#define LED_SW1 9   // D14
#define LED_SW2 8   // D15
#define LED_SW3 7   // D16
#define LED_SW4 6   // D17
#define LED_SW7 5   // D18
#define LED_SW9 0   // D7
#define LED_SW6 1   // D8
#define LED_SW8 2   // D9

#define DEBOUNCE_MS      6
#define UNASSIGNED_TEXT  "tejas.com"
#define HOST_TIMEOUT_MS  5000
