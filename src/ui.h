#pragma once
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <time.h>
#include "config.h"
#include "state.h"

static Adafruit_SSD1306 dispInfo(128, 64, &Wire, -1);
static Adafruit_SSD1306 dispSpot(128, 64, &Wire, -1);

static void tcaSelect(uint8_t ch) {
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

// Text that scrolls if wider than the screen
static void marquee(Adafruit_SSD1306 &d, const char *txt, int y, int size) {
  int w = strlen(txt) * 6 * size;
  d.setTextSize(size);
  d.setTextWrap(false);
  if (w <= 128) { d.setCursor(0, y); d.print(txt); return; }
  const int gap = 32;
  int off = (millis() / 35) % (w + gap);
  d.setCursor(-off, y);           d.print(txt);
  d.setCursor(-off + w + gap, y); d.print(txt);
}

static void fmtTime(char *out, size_t n, uint32_t s) {
  snprintf(out, n, "%lu:%02lu", (unsigned long)(s / 60), (unsigned long)(s % 60));
}

static void drawInfo(const AppState &s) {
  Adafruit_SSD1306 &d = dispInfo;
  d.clearDisplay();
  d.setTextColor(SSD1306_WHITE);
  d.setTextWrap(false);
  bool hostAlive = s.lastHostMs && (millis() - s.lastHostMs < HOST_TIMEOUT_MS);

  if (s.timeValid) {
    time_t t = s.epochBase + (millis() - s.millisBase) / 1000;
    struct tm tm; gmtime_r(&t, &tm);
    char buf[24];
    snprintf(buf, sizeof buf, "%02d:%02d", tm.tm_hour, tm.tm_min);
    d.setTextSize(3); d.setCursor(0, 0); d.print(buf);
    snprintf(buf, sizeof buf, "%02d", tm.tm_sec);
    d.setTextSize(2); d.setCursor(98, 8); d.print(buf);
    strftime(buf, sizeof buf, "%a %d %b %Y", &tm);
    d.setTextSize(1); d.setCursor(0, 28); d.print(buf);
  } else {
    d.setTextSize(3); d.setCursor(0, 0); d.print("--:--");
    d.setTextSize(1); d.setCursor(0, 28); d.print("waiting for PC...");
  }

  // volume row
  d.setTextSize(1);
  d.setCursor(0, 46); d.print("VOL");
  d.drawRect(24, 44, 76, 12, SSD1306_WHITE);
  if (!s.muted) d.fillRect(26, 46, (72 * s.volume) / 100, 8, SSD1306_WHITE);
  d.setCursor(104, 46);
  if (s.muted) d.print("MUTE"); else d.printf("%d", s.volume);
  d.setCursor(0, 57);
  d.print(hostAlive ? "PC linked" : "PC offline");
  d.display();
}

static void drawSpot(const AppState &s) {
  Adafruit_SSD1306 &d = dispSpot;
  d.clearDisplay();
  d.setTextColor(SSD1306_WHITE);
  d.setTextSize(1); d.setCursor(0, 0); d.print("SPOTIFY");
  // play / pause icon
  if (s.spotifyActive && s.playing) d.fillTriangle(118, 0, 118, 8, 125, 4, SSD1306_WHITE);
  else if (s.spotifyActive) { d.fillRect(117, 0, 3, 8, SSD1306_WHITE); d.fillRect(123, 0, 3, 8, SSD1306_WHITE); }

  if (!s.spotifyActive || !s.title[0]) {
    d.setTextSize(1); d.setCursor(0, 26); d.print("Nothing playing");
    d.display(); return;
  }
  marquee(d, s.title, 12, 2);
  marquee(d, s.artist, 32, 1);

  uint32_t pos = s.posSec;
  if (s.playing) pos += (millis() - s.posAtMs) / 1000;
  if (s.durSec && pos > s.durSec) pos = s.durSec;
  d.drawRect(0, 44, 128, 6, SSD1306_WHITE);
  if (s.durSec) d.fillRect(2, 46, (124 * pos) / s.durSec, 2, SSD1306_WHITE);
  char a[12], b[12];
  fmtTime(a, sizeof a, pos); fmtTime(b, sizeof b, s.durSec);
  d.setTextSize(1);
  d.setCursor(0, 54); d.print(a);
  d.setCursor(128 - strlen(b) * 6, 54); d.print(b);
  d.display();
}

static void uiTask(void *) {
  for (;;) {
    AppState snap;
    { StateLock l; snap = gState; }
    tcaSelect(TCA_CH_INFO);    drawInfo(snap);
    tcaSelect(TCA_CH_SPOTIFY); drawSpot(snap);
    vTaskDelay(pdMS_TO_TICKS(60));
  }
}

// Runs the OLEDs on core 0 so key scanning on core 1 never stalls.
inline bool uiBegin() {
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);
  if (PIN_TCA_RESET >= 0) {
    pinMode(PIN_TCA_RESET, OUTPUT);
    digitalWrite(PIN_TCA_RESET, LOW);  delay(5);
    digitalWrite(PIN_TCA_RESET, HIGH); delay(5);
  }
  bool ok = true;
  tcaSelect(TCA_CH_INFO);    ok &= dispInfo.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  tcaSelect(TCA_CH_SPOTIFY); ok &= dispSpot.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (ok) xTaskCreatePinnedToCore(uiTask, "ui", 6144, nullptr, 1, nullptr, 0);
  return ok;
}
