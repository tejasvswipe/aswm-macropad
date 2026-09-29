#pragma once
#include <Adafruit_NeoPixel.h>
#include "config.h"

static Adafruit_NeoPixel strip(LED_COUNT, PIN_LED_DATA, NEO_GRB + NEO_KHZ800);
static uint32_t flashUntil[LED_COUNT];

inline void ledsBegin() {
  strip.begin();
  strip.setBrightness(LED_BRIGHTNESS);
  strip.show();
}

inline void ledFlash(uint8_t i) {
  if (i < LED_COUNT) flashUntil[i] = millis() + 180;
}

// Slow rainbow idle, white flash on key press, red breathing when muted.
inline void ledsUpdate(bool muted) {
  static uint32_t last = 0;
  uint32_t now = millis();
  if (now - last < 20) return;
  last = now;
  for (uint8_t i = 0; i < LED_COUNT; i++) {
    uint32_t c;
    if (now < flashUntil[i]) {
      c = strip.Color(255, 255, 255);
    } else if (muted) {
      uint8_t b = 25 + (uint8_t)((sinf(now / 350.0f) + 1.0f) * 45.0f);
      c = strip.Color(b, 0, 0);
    } else {
      uint16_t hue = (uint16_t)(now * 6 + i * (65536 / LED_COUNT));
      c = strip.gamma32(strip.ColorHSV(hue, 255, 110));
    }
    strip.setPixelColor(i, c);
  }
  strip.show();
}
