#pragma once
#include <Arduino.h>
#include <freertos/semphr.h>

struct AppState {
  int      volume = 50;          // 0-100
  bool     muted = false;
  uint32_t volTouchedMs = 0;     // last local encoder/mute action
  bool     timeValid = false;
  uint32_t epochBase = 0;        // LOCAL time (secs) at millisBase
  uint32_t millisBase = 0;
  bool     spotifyActive = false;
  bool     playing = false;
  uint32_t posSec = 0, durSec = 0, posAtMs = 0;
  char     title[64]  = "";
  char     artist[48] = "";
  uint32_t lastHostMs = 0;       // 0 = never heard from PC
};

extern AppState gState;
extern SemaphoreHandle_t gStateMtx;

struct StateLock {
  StateLock()  { xSemaphoreTake(gStateMtx, portMAX_DELAY); }
  ~StateLock() { xSemaphoreGive(gStateMtx); }
};
