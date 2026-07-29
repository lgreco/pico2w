"""
examples/touch_basic.py — Print touch coordinates and gestures to the REPL.

Copy lib/cst816s.py to the Pico before running this script.
Tap, swipe, or long-press the screen and watch the output.
"""

import time
from machine import I2C, Pin
from lib.cst816s import CST816S

# --------------------------------------------------------------------------- #
# Pin configuration — adjust to match your wiring                             #
# --------------------------------------------------------------------------- #
PIN_SDA = 4
PIN_SCL = 5
PIN_INT = 21   # active-low interrupt from CST816S
PIN_RST = 22   # reset line to CST816S

# --------------------------------------------------------------------------- #
# Initialise I²C and touch controller                                          #
# --------------------------------------------------------------------------- #
i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400_000)
touch = CST816S(
    i2c,
    int_pin=Pin(PIN_INT, Pin.IN),
    rst_pin=Pin(PIN_RST),
)

print(f"CST816S  chip_id=0x{touch.chip_id:02X}"
      f"  fw_version=0x{touch.firmware_version:02X}")
print("Touch the screen — press Ctrl-C to stop\n")

try:
    while True:
        if touch.available():
            x, y, gesture = touch.read()
            print(f"  x={x:3d}  y={y:3d}  gesture={gesture}")
        time.sleep_ms(10)
except KeyboardInterrupt:
    print("Stopped.")
