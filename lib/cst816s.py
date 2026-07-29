"""
CST816S capacitive touch controller driver for MicroPython (I²C).

The CST816S is a single-touch capacitive controller commonly paired with
small round or square TFT LCD modules.  It communicates over I²C at address
0x15 and optionally signals new data via an active-low interrupt pin.

Usage::

    from machine import I2C, Pin
    from lib.cst816s import CST816S

    i2c   = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
    touch = CST816S(i2c, int_pin=Pin(21, Pin.IN), rst_pin=Pin(22))

    while True:
        if touch.available():
            x, y, gesture = touch.read()
            print(f"Touch  x={x}  y={y}  gesture={gesture!r}")
"""

import time
from micropython import const

# I²C address (fixed in hardware)
_CST816S_ADDR = const(0x15)

# Register addresses
_REG_GESTURE    = const(0x01)
_REG_FINGER_NUM = const(0x02)
_REG_XPOS_H     = const(0x03)
_REG_XPOS_L     = const(0x04)
_REG_YPOS_H     = const(0x05)
_REG_YPOS_L     = const(0x06)
_REG_CHIP_ID    = const(0xA7)
_REG_PROJ_ID    = const(0xA8)
_REG_FW_VERSION = const(0xA9)
_REG_SLEEP_MODE = const(0xE5)
_REG_IRQ_CTL    = const(0xFA)
_REG_AUTO_RESET = const(0xFB)
_REG_LONG_PRESS = const(0xFC)
_REG_MOTION_MASK= const(0xEC)

# Gesture codes reported in _REG_GESTURE
GESTURE_NONE       = 0x00
GESTURE_SWIPE_UP   = 0x01
GESTURE_SWIPE_DOWN = 0x02
GESTURE_SWIPE_LEFT = 0x03
GESTURE_SWIPE_RIGHT= 0x04
GESTURE_CLICK      = 0x05
GESTURE_DCLICK     = 0x0B
GESTURE_LONG_PRESS = 0x0C

_GESTURE_NAMES = {
    GESTURE_NONE:        "none",
    GESTURE_SWIPE_UP:    "swipe_up",
    GESTURE_SWIPE_DOWN:  "swipe_down",
    GESTURE_SWIPE_LEFT:  "swipe_left",
    GESTURE_SWIPE_RIGHT: "swipe_right",
    GESTURE_CLICK:       "click",
    GESTURE_DCLICK:      "double_click",
    GESTURE_LONG_PRESS:  "long_press",
}


class CST816S:
    """Driver for the CST816S capacitive single-touch controller."""

    def __init__(self, i2c, *, int_pin=None, rst_pin=None,
                 addr: int = _CST816S_ADDR):
        self._i2c     = i2c
        self._addr    = addr
        self._int_pin = int_pin
        self._rst_pin = rst_pin
        self._touched = False

        if self._rst_pin is not None:
            self._reset()

        if self._int_pin is not None:
            # Use falling-edge IRQ to set an internal flag
            self._int_pin.irq(
                trigger=self._int_pin.IRQ_FALLING,
                handler=self._irq_handler,
            )

    # ----------------------------------------------------------------------- #
    # Internal helpers                                                         #
    # ----------------------------------------------------------------------- #

    def _reset(self) -> None:
        from machine import Pin  # noqa: PLC0415
        self._rst_pin.init(Pin.OUT)
        self._rst_pin(0)
        time.sleep_ms(10)
        self._rst_pin(1)
        time.sleep_ms(50)

    def _irq_handler(self, pin) -> None:  # noqa: ARG002
        self._touched = True

    def _read_reg(self, reg: int, length: int = 1) -> bytes:
        self._i2c.writeto(self._addr, bytes([reg]))
        return self._i2c.readfrom(self._addr, length)

    def _write_reg(self, reg: int, value: int) -> None:
        self._i2c.writeto(self._addr, bytes([reg, value]))

    # ----------------------------------------------------------------------- #
    # Public API                                                               #
    # ----------------------------------------------------------------------- #

    @property
    def chip_id(self) -> int:
        """Return the chip identifier byte (should be 0xB5 for CST816S)."""
        return self._read_reg(_REG_CHIP_ID)[0]

    @property
    def firmware_version(self) -> int:
        """Return the firmware version byte."""
        return self._read_reg(_REG_FW_VERSION)[0]

    def available(self) -> bool:
        """
        Return ``True`` if a new touch event is waiting.

        When an interrupt pin is configured this is IRQ-driven (fast);
        otherwise the finger-count register is polled directly.
        """
        if self._int_pin is not None:
            if self._touched:
                self._touched = False
                return True
            return False
        # Polled fallback
        return self._read_reg(_REG_FINGER_NUM)[0] > 0

    def read(self) -> tuple[int, int, str]:
        """
        Read the latest touch position and gesture.

        Returns a ``(x, y, gesture_name)`` tuple.  ``gesture_name`` is a
        human-readable string such as ``"click"`` or ``"swipe_up"``.
        Returns ``(0, 0, "none")`` when no finger is detected.
        """
        buf = self._read_reg(_REG_GESTURE, 6)
        gesture_code = buf[0]
        # finger_num  = buf[1]   (unused for single-touch)
        x = ((buf[2] & 0x0F) << 8) | buf[3]
        y = ((buf[4] & 0x0F) << 8) | buf[5]
        gesture_name = _GESTURE_NAMES.get(gesture_code, f"0x{gesture_code:02X}")
        return x, y, gesture_name

    def sleep(self) -> None:
        """Put the controller into low-power sleep mode."""
        self._write_reg(_REG_SLEEP_MODE, 0x03)

    def wake(self) -> None:
        """Wake the controller from sleep (hardware reset required)."""
        if self._rst_pin is not None:
            self._reset()

    def set_irq_mode(self, mode: int = 0) -> None:
        """
        Configure the INT pin behaviour.

        ``mode`` values:
          * ``0`` – low-pulse when touch detected (default)
          * ``1`` – rising-edge
          * ``2`` – falling-edge
          * ``3`` – periodic low-pulse (heartbeat)
        """
        self._write_reg(_REG_IRQ_CTL, mode & 0x0F)
