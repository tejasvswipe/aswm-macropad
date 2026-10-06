"""Optional status sender for a future display-equipped board.

The shipped PCB has no display, so this is intentionally not required for HID
operation. It sends a simple line once per second over the CircuitPython USB
serial port for a later OLED/display revision.
"""
import argparse
import datetime as dt
import time

import serial

parser = argparse.ArgumentParser()
parser.add_argument("port", help="CircuitPython USB serial port, e.g. COM7")
parser.add_argument("--baud", type=int, default=115200)
args = parser.parse_args()

with serial.Serial(args.port, args.baud, timeout=1) as device:
    while True:
        now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        device.write(f"T\t{now}\n".encode())
        time.sleep(1)
