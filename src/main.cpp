// Tejas Macropad firmware - ESP32-S3 (Arduino-ESP32 core 3.x)
//  Keys : SW1 Copy | SW2 Paste | SW3 Win+1 | SW4 Win+2 | SW7 Win+3
//         SW6/SW8/SW9 -> types "tejas.com"
//  Knob : rotate = volume, press = mute
//  OLED : DS1 time+volume, DS2 Spotify mini player (data from host/companion.py)
#include <Arduino.h>
#include "USB.h"
#include "USBHIDKeyboard.h"
#include "USBHIDConsumerControl.h"
#include "driver/gpio.h"
#include "config.h"
#include "state.h"
#include "leds.h"
#include "ui.h"

USBHIDKeyboard Keyboard;
USBHIDConsumerControl ConsumerControl;
AppState gState;
SemaphoreHandle_t gStateMtx;

// ---------------------------------------------------------------- buttons
class Button {
 public:
  explicit Button(uint8_t p) : pin(p) {}
  void begin() { pinMode(pin, INPUT_PULLUP); }
  bool pressed() {                      // true once per debounced press
    bool r = (digitalRead(pin) == LOW);
    uint32_t now = millis();
    if (r != raw) { raw = r; t = now; }
    else if (r != stable && now - t >= DEBOUNCE_MS) {
      stable = r;
      return r;
    }
    return false;
  }
 private:
  uint8_t pin; bool raw = false, stable = false; uint32_t t = 0;
};

enum class Act : uint8_t { Copy, Paste, WinNum, TypeText };
struct KeyDef { const char *name; uint8_t pin; Act act; char arg; uint8_t led; };

static const KeyDef KEYS[] = {
  {"SW1", PIN_SW1, Act::Copy,     0,   LED_SW1},
  {"SW2", PIN_SW2, Act::Paste,    0,   LED_SW2},
  {"SW3", PIN_SW3, Act::WinNum,   '1', LED_SW3},
  {"SW4", PIN_SW4, Act::WinNum,   '2', LED_SW4},
  {"SW7", PIN_SW7, Act::WinNum,   '3', LED_SW7},
  {"SW6", PIN_SW6, Act::TypeText, 0,   LED_SW6},
  {"SW8", PIN_SW8, Act::TypeText, 0,   LED_SW8},
  {"SW9", PIN_SW9, Act::TypeText, 0,   LED_SW9},
};
static const size_t NKEYS = sizeof(KEYS) / sizeof(KEYS[0]);
static Button *btn[NKEYS];
static Button encBtn(PIN_ENC_SW);

static void chord(uint8_t mod, char key) {
  Keyboard.press(mod);
  Keyboard.press(key);
  delay(15);
  Keyboard.releaseAll();
}

static void fire(const KeyDef &k) {
  ledFlash(k.led);
  switch (k.act) {
    case Act::Copy:     chord(KEY_LEFT_CTRL, 'c'); break;
    case Act::Paste:    chord(KEY_LEFT_CTRL, 'v'); break;
    case Act::WinNum:   chord(KEY_LEFT_GUI, k.arg); break;
    case Act::TypeText: Keyboard.print(UNASSIGNED_TEXT); break;
  }
}

// ---------------------------------------------------------------- encoder
static volatile int32_t encAcc = 0;
static volatile uint8_t encHist = 0;
static portMUX_TYPE encMux = portMUX_INITIALIZER_UNLOCKED;
// quadrature transition table: index = (prev<<2)|curr
static const int8_t ENC_TAB[16] = {0,-1,1,0, 1,0,0,-1, -1,0,0,1, 0,1,-1,0};

static void IRAM_ATTR encISR() {
  uint8_t cur = (gpio_get_level((gpio_num_t)PIN_ENC_A) << 1) |
                 gpio_get_level((gpio_num_t)PIN_ENC_B);
  portENTER_CRITICAL_ISR(&encMux);
  encHist = ((encHist << 2) | cur) & 0x0F;
  encAcc += ENC_TAB[encHist];
  portEXIT_CRITICAL_ISR(&encMux);
}

static int encTakeSteps() {
  int steps = 0;
  portENTER_CRITICAL(&encMux);
  steps = encAcc / ENC_TRANSITIONS_PER_DETENT;
  encAcc -= steps * ENC_TRANSITIONS_PER_DETENT;
  portEXIT_CRITICAL(&encMux);
  return ENC_INVERT ? -steps : steps;
}

static void volumeStep(int dir) {
  ConsumerControl.press(dir > 0 ? CONSUMER_CONTROL_VOLUME_INCREMENT
                                : CONSUMER_CONTROL_VOLUME_DECREMENT);
  ConsumerControl.release();
  StateLock l;
  gState.volume = constrain(gState.volume + dir * VOLUME_STEP, 0, 100);
  gState.muted = false;
  gState.volTouchedMs = millis();
}

static void toggleMute() {
  ConsumerControl.press(CONSUMER_CONTROL_MUTE);
  ConsumerControl.release();
  StateLock l;
  gState.muted = !gState.muted;
  gState.volTouchedMs = millis();
}

// ---------------------------------------------------------------- host link
// Lines from PC, TAB separated, '\n' terminated:
//   T <local_epoch_secs>
//   V <volume 0-100> <muted 0|1>
//   S <playing 0|1> <pos_s> <dur_s> <title> <artist>
static char rxBuf[256];
static size_t rxLen = 0;

static int split(char *s, char **f, int maxf) {
  int n = 0; f[n++] = s;
  for (char *p = s; *p && n < maxf; p++)
    if (*p == '\t') { *p = 0; f[n++] = p + 1; }
  return n;
}

static void handleLine(char *line) {
  char *f[8];
  int n = split(line, f, 8);
  StateLock l;
  if (f[0][0] == 'T' && n >= 2) {
    gState.epochBase = strtoul(f[1], nullptr, 10);
    gState.millisBase = millis();
    gState.timeValid = true;
  } else if (f[0][0] == 'V' && n >= 3) {
    if (millis() - gState.volTouchedMs > 400) {      // don't fight the knob
      gState.volume = constrain(atoi(f[1]), 0, 100);
      gState.muted = atoi(f[2]) != 0;
    }
  } else if (f[0][0] == 'S' && n >= 6) {
    gState.playing = atoi(f[1]) != 0;
    gState.posSec = strtoul(f[2], nullptr, 10);
    gState.durSec = strtoul(f[3], nullptr, 10);
    gState.posAtMs = millis();
    strlcpy(gState.title, f[4], sizeof gState.title);
    strlcpy(gState.artist, f[5], sizeof gState.artist);
    gState.spotifyActive = gState.title[0] != 0;
  } else {
    return;
  }
  gState.lastHostMs = millis();
}

static void pollSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { rxBuf[rxLen] = 0; if (rxLen) handleLine(rxBuf); rxLen = 0; }
    else if (c != '\r' && rxLen < sizeof(rxBuf) - 1) rxBuf[rxLen++] = c;
  }
}

// ---------------------------------------------------------------- Arduino
void setup() {
  gStateMtx = xSemaphoreCreateMutex();

  Keyboard.begin();
  ConsumerControl.begin();
  USB.manufacturerName("Tejas");
  USB.productName("Tejas Macropad");
  USB.begin();
  Serial.begin(115200);

  for (size_t i = 0; i < NKEYS; i++) { btn[i] = new Button(KEYS[i].pin); btn[i]->begin(); }
  encBtn.begin();
  pinMode(PIN_ENC_A, INPUT_PULLUP);
  pinMode(PIN_ENC_B, INPUT_PULLUP);
  encHist = (digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B);
  attachInterrupt(PIN_ENC_A, encISR, CHANGE);
  attachInterrupt(PIN_ENC_B, encISR, CHANGE);

  ledsBegin();
  uiBegin();   // if false, check I2C wiring / mux channel / OLED address
}

void loop() {
  for (size_t i = 0; i < NKEYS; i++)
    if (btn[i]->pressed()) fire(KEYS[i]);

  if (encBtn.pressed()) toggleMute();

  int steps = encTakeSteps();
  if (steps > 8) steps = 8; else if (steps < -8) steps = -8;
  for (; steps > 0; steps--) volumeStep(+1);
  for (; steps < 0; steps++) volumeStep(-1);

  pollSerial();
  bool muted; { StateLock l; muted = gState.muted; }
  ledsUpdate(muted);
  delay(1);
}
