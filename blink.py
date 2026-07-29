"""
blink.py — Blink the onboard LED on the Raspberry Pi Pico 2W.

Run this as a standalone script to verify MicroPython is working.
Press Ctrl-C in the REPL to stop.
"""

import time
from machine import Pin

LED_PIN = "LED"   # "LED" is the onboard LED alias on Pico W / Pico 2W

led = Pin(LED_PIN, Pin.OUT)

print("Blinking onboard LED — press Ctrl-C to stop")

try:
    while True:
        led.toggle()
        time.sleep(0.5)
except KeyboardInterrupt:
    led.off()
    print("Stopped.")
