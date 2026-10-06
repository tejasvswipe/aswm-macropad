import usb_hid
from usb_hid import Device

# Keep only the interfaces this macropad uses.
usb_hid.enable((Device.KEYBOARD, Device.CONSUMER_CONTROL))
