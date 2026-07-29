"""
examples/display_basic.py — Draw shapes and text on the GC9A01 round LCD.

Copy lib/gc9a01.py to the Pico before running this script.
"""

import time
from machine import SPI, Pin
from lib.gc9a01 import GC9A01, color565

# --------------------------------------------------------------------------- #
# Pin configuration — adjust to match your wiring                             #
# --------------------------------------------------------------------------- #
PIN_SCK  = 18
PIN_MOSI = 19
PIN_CS   = 17
PIN_DC   = 20
PIN_RST  = 15
PIN_BL   = 14

# --------------------------------------------------------------------------- #
# Initialise SPI and display                                                   #
# --------------------------------------------------------------------------- #
spi = SPI(0, baudrate=40_000_000, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))
display = GC9A01(
    spi,
    cs=Pin(PIN_CS),
    dc=Pin(PIN_DC),
    rst=Pin(PIN_RST),
    bl=Pin(PIN_BL),
)

# --------------------------------------------------------------------------- #
# Demo — fill screen, draw shapes, show text                                  #
# --------------------------------------------------------------------------- #
BLACK  = color565(0,   0,   0)
WHITE  = color565(255, 255, 255)
RED    = color565(255, 0,   0)
GREEN  = color565(0,   200, 0)
BLUE   = color565(0,   0,   255)
YELLOW = color565(255, 220, 0)
CYAN   = color565(0,   220, 220)

CX, CY = 120, 120   # display centre

print("Display basic demo — drawing shapes")

# Black background
display.fill(BLACK)
display.show()
time.sleep(0.5)

# Concentric filled circles (colour wheel)
for radius, colour in [
    (110, BLUE),
    (80,  CYAN),
    (55,  GREEN),
    (35,  YELLOW),
    (18,  RED),
]:
    display.fill_circle(CX, CY, radius, colour)

# White border circle
display.circle(CX, CY, 115, WHITE)

# Text in the centre
label = "Pico 2W"
# Each character is 8 px wide with the built-in font
x = CX - len(label) * 4   # rough horizontal centre
display.text(label, x, CY - 8, WHITE)
display.text("52PI kit", CX - 32, CY + 8, WHITE)

display.show()
print("Done — display is showing the demo image.")
