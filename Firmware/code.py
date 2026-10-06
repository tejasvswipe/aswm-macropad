import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# KiCad schematic pinout: ROW0..3 = D0..D3, COL0..3 = D4..D7.
ROWS = (board.D0, board.D1, board.D2, board.D3)
COLS = (board.D4, board.D5, board.D6, board.D7)
ENC_A, ENC_B, ENC_SW = board.D8, board.D9, board.D10

keyboard = Keyboard(usb_hid.devices)
consumer = ConsumerControl(usb_hid.devices)

rows = []
for pin in ROWS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.UP
    rows.append(io)

cols = []
for pin in COLS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.OUTPUT
    io.value = True
    cols.append(io)

enc_a = digitalio.DigitalInOut(ENC_A)
enc_a.direction = digitalio.Direction.INPUT
enc_a.pull = digitalio.Pull.UP
enc_b = digitalio.DigitalInOut(ENC_B)
enc_b.direction = digitalio.Direction.INPUT
enc_b.pull = digitalio.Pull.UP
enc_sw = digitalio.DigitalInOut(ENC_SW)
enc_sw.direction = digitalio.Direction.INPUT
enc_sw.pull = digitalio.Pull.UP

# SW1..SW16: copy, paste, Chrome tab controls, then Windows workspaces.
# The matrix is scanned row-major: SW1 = row 0/col 0.
KEYMAP = {
    0: (Keycode.CONTROL, Keycode.C),
    1: (Keycode.CONTROL, Keycode.V),
    2: (Keycode.CONTROL, Keycode.TAB),
    3: (Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB),
    4: (Keycode.CONTROL, Keycode.T),
    5: (Keycode.CONTROL, Keycode.W),
    6: (Keycode.CONTROL, Keycode.L),
    7: (Keycode.GUI, Keycode.ONE),
    8: (Keycode.GUI, Keycode.TWO),
    9: (Keycode.GUI, Keycode.THREE),
    10: (Keycode.GUI, Keycode.FOUR),
    11: (Keycode.GUI, Keycode.FIVE),
    12: (Keycode.GUI, Keycode.SIX),
    13: (Keycode.GUI, Keycode.SEVEN),
    14: (Keycode.GUI, Keycode.EIGHT),
    15: (Keycode.GUI, Keycode.NINE),
}

last_keys = [False] * 16
last_scan = 0
last_encoder = (enc_a.value << 1) | enc_b.value
last_encoder_step = 0
last_encoder_time = 0
last_encoder_switch = True
last_switch_time = 0

# Quadrature transitions. Direction may be reversed by swapping ENC_A/ENC_B.
QUAD = {
    (0, 1): 1, (1, 3): 1, (3, 2): 1, (2, 0): 1,
    (0, 2): -1, (2, 3): -1, (3, 1): -1, (1, 0): -1,
}


def tap(combo):
    for key in combo:
        keyboard.press(key)
    for key in reversed(combo):
        keyboard.release(key)


def scan_keys(now):
    global last_scan
    if now - last_scan < 0.002:
        return
    last_scan = now
    current = [False] * 16
    for col, output in enumerate(cols):
        output.value = False
        time.sleep(0.00015)
        for row, input_pin in enumerate(rows):
            current[row * 4 + col] = not input_pin.value
        output.value = True
    for index, pressed in enumerate(current):
        if pressed and not last_keys[index]:
            tap(KEYMAP[index])
    last_keys[:] = current


def scan_encoder(now):
    global last_encoder, last_encoder_step, last_encoder_time
    state = (enc_a.value << 1) | enc_b.value
    delta = QUAD.get((last_encoder, state), 0)
    last_encoder = state
    if delta:
        last_encoder_step += delta
        if abs(last_encoder_step) >= 4 and now - last_encoder_time > 0.03:
            if last_encoder_step > 0:
                consumer.send(ConsumerControlCode.VOLUME_INCREMENT)
            else:
                consumer.send(ConsumerControlCode.VOLUME_DECREMENT)
            last_encoder_step = 0
            last_encoder_time = now


def scan_encoder_switch(now):
    global last_encoder_switch, last_switch_time
    pressed = not enc_sw.value
    if pressed and last_encoder_switch and now - last_switch_time > 0.18:
        # Works with Spotify and other media players through the OS media key.
        consumer.send(ConsumerControlCode.PLAY_PAUSE)
        last_switch_time = now
    last_encoder_switch = pressed


while True:
    now = time.monotonic()
    scan_keys(now)
    scan_encoder(now)
    scan_encoder_switch(now)
    time.sleep(0.001)
