"""
main.py — Interactive startup demo for the Pico 2W + 52PI kit.

This script runs automatically when the Pico 2W boots (MicroPython looks for
main.py on the filesystem).  It shows a splash screen and then enters a simple
touch-driven colour-picker demo.

Copy the entire lib/ directory to the Pico before deploying this file.
"""

import time
from machine import SPI, I2C, Pin
from lib.gc9a01 import GC9A01, color565
from lib.cst816s import CST816S

# --------------------------------------------------------------------------- #
# Pin configuration                                                            #
# --------------------------------------------------------------------------- #
PIN_SCK   = 18
PIN_MOSI  = 19
PIN_CS    = 17
PIN_DC    = 20
PIN_RST_D = 15   # display reset
PIN_BL    = 14

PIN_SDA   = 4
PIN_SCL   = 5
PIN_INT   = 21
PIN_RST_T = 22   # touch reset

# --------------------------------------------------------------------------- #
# Colours                                                                      #
# --------------------------------------------------------------------------- #
BLACK  = color565(0,   0,   0)
WHITE  = color565(255, 255, 255)
RED    = color565(220, 0,   0)
GREEN  = color565(0,   180, 0)
BLUE   = color565(0,   80,  220)
YELLOW = color565(240, 200, 0)
CYAN   = color565(0,   200, 220)
GRAY   = color565(80,  80,  80)

PALETTE = [WHITE, RED, YELLOW, GREEN, CYAN, BLUE]
BRUSH   = 4   # paint radius (pixels)

# --------------------------------------------------------------------------- #
# Initialise hardware                                                          #
# --------------------------------------------------------------------------- #
spi = SPI(0, baudrate=40_000_000, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))
display = GC9A01(spi, cs=Pin(PIN_CS), dc=Pin(PIN_DC),
                 rst=Pin(PIN_RST_D), bl=Pin(PIN_BL))

i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400_000)
touch = CST816S(i2c, int_pin=Pin(PIN_INT, Pin.IN), rst_pin=Pin(PIN_RST_T))

# --------------------------------------------------------------------------- #
# Splash screen                                                                #
# --------------------------------------------------------------------------- #

def splash() -> None:
    CX, CY = 120, 120
    display.fill(BLACK)
    display.fill_circle(CX, CY, 115, BLUE)
    display.fill_circle(CX, CY, 100, BLACK)
    display.circle(CX, CY, 115, CYAN)
    display.text("Pico 2W", CX - 28, CY - 12, WHITE)
    display.text("52PI kit", CX - 32,  CY + 4,  CYAN)
    display.show()
    time.sleep(2)


# --------------------------------------------------------------------------- #
# HUD helpers                                                                  #
# --------------------------------------------------------------------------- #

def _draw_palette(selected: int) -> None:
    """Draw colour swatches along the bottom of the screen."""
    sw = 30   # swatch width/height
    gap = 5
    total = len(PALETTE) * sw + (len(PALETTE) - 1) * gap
    start_x = (240 - total) // 2
    y = 240 - sw - 8
    for i, col in enumerate(PALETTE):
        x = start_x + i * (sw + gap)
        display.fill_rect(x, y, sw, sw, col)
        if i == selected:
            display.rect(x - 2, y - 2, sw + 4, sw + 4, WHITE)
        else:
            display.rect(x, y, sw, sw, GRAY)


def _swatch_hit(px: int, py: int) -> int:
    """Return palette index if (px, py) is inside a swatch, else -1."""
    sw = 30
    gap = 5
    total = len(PALETTE) * sw + (len(PALETTE) - 1) * gap
    start_x = (240 - total) // 2
    y_top = 240 - sw - 8
    if py < y_top or py > y_top + sw:
        return -1
    for i in range(len(PALETTE)):
        x = start_x + i * (sw + gap)
        if x <= px <= x + sw:
            return i
    return -1


# --------------------------------------------------------------------------- #
# Main paint loop                                                              #
# --------------------------------------------------------------------------- #

def run() -> None:
    colour_idx = 0
    display.fill(BLACK)
    _draw_palette(colour_idx)
    display.show()

    print("Main demo running — touch to draw, tap a swatch to change colour")
    print("Long-press to clear the canvas\n")

    while True:
        if touch.available():
            x, y, gesture = touch.read()

            if gesture == "long_press":
                # Clear canvas but keep palette
                display.fill_rect(0, 0, 240, 200, BLACK)
                _draw_palette(colour_idx)
                display.show()
                continue

            # Check if a palette swatch was tapped
            hit = _swatch_hit(x, y)
            if hit >= 0:
                colour_idx = hit
                _draw_palette(colour_idx)
                display.show()
                continue

            # Paint a dot
            if y < 220:   # don't paint over the palette row
                display.fill_circle(x, y, BRUSH, PALETTE[colour_idx])
                display.show()

        time.sleep_ms(5)


# --------------------------------------------------------------------------- #
# Entry point                                                                  #
# --------------------------------------------------------------------------- #
splash()
run()
