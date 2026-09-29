"""
Tejas Macropad - Windows companion.
Sends local time, real system volume/mute and Spotify now-playing to the pad
over its USB-CDC serial port.

  pip install -r requirements.txt
  python companion.py            # auto-detects the pad (Espressif VID 0x303A)
  python companion.py --port COM7
Run with pythonw.exe from Task Scheduler / shell:startup to launch at login.
"""
import argparse, asyncio, time, unicodedata
import serial
from serial.tools import list_ports

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as SessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)

def ascii_clean(s: str, n: int) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "replace").decode()
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")[:n]

def find_port():
    for p in list_ports.comports():
        if p.vid == 0x303A:
            return p.device
    return None

def endpoint_volume():
    dev = AudioUtilities.GetSpeakers()
    if hasattr(dev, "EndpointVolume"):          # newer pycaw
        return dev.EndpointVolume
    iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(iface, POINTER(IAudioEndpointVolume))

def read_volume():
    ev = endpoint_volume()
    return round(ev.GetMasterVolumeLevelScalar() * 100), int(ev.GetMute())

async def read_spotify(mgr):
    sessions = list(mgr.get_sessions())
    ses = next((s for s in sessions
                if "spotify" in (s.source_app_user_model_id or "").lower()), None)
    if ses is None:
        return None
    props = await ses.try_get_media_properties_async()
    tl = ses.get_timeline_properties()
    playing = ses.get_playback_info().playback_status == PlaybackStatus.PLAYING
    dur = int((tl.end_time - tl.start_time).total_seconds())
    pos = int(tl.position.total_seconds())
    return playing, pos, dur, props.title or "", props.artist or ""

async def run(port):
    mgr = await SessionManager.request_async()
    while True:
        try:
            with serial.Serial(port, 115200, timeout=0, write_timeout=1) as ser:
                print(f"connected on {port}")
                last_t = last_s = 0.0
                while True:
                    now = time.time()
                    if now - last_t >= 1.0:
                        local = int(now) + time.localtime().tm_gmtoff
                        ser.write(f"T\t{local}\n".encode()); last_t = now
                    try:
                        v, m = read_volume()
                        ser.write(f"V\t{v}\t{m}\n".encode())
                    except Exception as e:
                        print("volume:", e)
                    if now - last_s >= 1.0:
                        last_s = now
                        try:
                            sp = await read_spotify(mgr)
                        except Exception as e:
                            print("spotify:", e); sp = None
                        if sp:
                            pl, pos, dur, ti, ar = sp
                            ser.write(f"S\t{int(pl)}\t{pos}\t{dur}\t"
                                      f"{ascii_clean(ti,63)}\t{ascii_clean(ar,47)}\n".encode())
                        else:
                            ser.write(b"S\t0\t0\t0\t\t\n")
                    ser.read(256)                       # drain anything the pad sends
                    await asyncio.sleep(0.25)
        except (serial.SerialException, OSError):
            print("pad not found / disconnected, retrying...")
            await asyncio.sleep(2)
            port = find_port() or port

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--port")
    a = ap.parse_args()
    port = a.port or find_port()
    while not port:
        print("waiting for macropad..."); time.sleep(2); port = find_port()
    asyncio.run(run(port))
