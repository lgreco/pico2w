"""
examples/touch_draw.py — Draw on the round LCD by dragging your finger.

Copy lib/gc9a01.py and lib/cst816s.py to the Pico before running this script.

Controls:
  • Drag  — paint pixels with the current colour
  • Swipe left/right — cycle through a palette of colours
  • Long press (≥ 0.8 s) — clear the screen
"""

import time
from machine import SPI, I2C, Pin
from lib.gc9a01 import GC9A01, color565
from lib.cst816s import CST816S

# --------------------------------------------------------------------------- #
# Pin configuration — adjust to match your wiring                             #
# --------------------------------------------------------------------------- #
PIN_SCK  = 18
PIN_MOSI = 19
PIN_CS   = 17
PIN_DC   = 20
PIN_RST  = 15
PIN_BL   = 14

PIN_SDA  = 4
PIN_SCL  = 5
PIN_INT  = 21
PIN_RST_T = 22

# --------------------------------------------------------------------------- #
# Colour palette                                                               #
# --------------------------------------------------------------------------- #
PALETTE = [
    color565(255, 255, 255),  # white
    color565(255, 0,   0),    # red
    color565(255, 165, 0),    # orange
    color565(255, 220, 0),    # yellow
    color565(0,   200, 0),    # green
    color565(0,   180, 255),  # sky blue
    color565(0,   0,   255),  # blue
    color565(180, 0,   255),  # violet
]
BLACK = color565(0, 0, 0)

# --------------------------------------------------------------------------- #
# Initialise peripherals                                                       #
# --------------------------------------------------------------------------- #
spi = SPI(0, baudrate=40_000_000, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))
display = GC9A01(spi, cs=Pin(PIN_CS), dc=Pin(PIN_DC),
                 rst=Pin(PIN_RST), bl=Pin(PIN_BL))

i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400_000)
touch = CST816S(i2c, int_pin=Pin(PIN_INT, Pin.IN), rst_pin=Pin(PIN_RST_T))

# --------------------------------------------------------------------------- #
# State                                                                        #
# --------------------------------------------------------------------------- #
colour_idx = 0
brush_size = 3   # radius in pixels

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def clear_screen() -> None:
    display.fill(BLACK)
    display.show()
    print("Screen cleared")


def draw_colour_indicator(idx: int) -> None:
    """Show a small swatch at the top-right corner."""
    display.fill_rect(215, 5, 20, 20, PALETTE[idx])
    display.rect(215, 5, 20, 20, color565(200, 200, 200))


# --------------------------------------------------------------------------- #
# Main loop                                                                    #
# --------------------------------------------------------------------------- #
clear_screen()
draw_colour_indicator(colour_idx)
display.show()

print("Touch-draw demo — drag to draw, swipe L/R for colour, long-press to clear")
print("Press Ctrl-C to quit\n")

try:
    while True:
        if touch.available():
            x, y, gesture = touch.read()

            if gesture == "swipe_right":
                colour_idx = (colour_idx + 1) % len(PALETTE)
                draw_colour_indicator(colour_idx)
                display.show()
                print(f"Colour → index {colour_idx}")

            elif gesture == "swipe_left":
                colour_idx = (colour_idx - 1) % len(PALETTE)
                draw_colour_indicator(colour_idx)
                display.show()
                print(f"Colour ← index {colour_idx}")

            elif gesture == "long_press":
                clear_screen()
                draw_colour_indicator(colour_idx)
                display.show()

            else:
                # Regular touch / drag — paint a filled circle at (x, y)
                display.fill_circle(x, y, brush_size, PALETTE[colour_idx])
                display.show()

        time.sleep_ms(5)

except KeyboardInterrupt:
    print("Stopped.")
