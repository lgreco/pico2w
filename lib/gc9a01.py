"""
GC9A01 round-LCD driver for MicroPython (SPI).

Tested on: Raspberry Pi Pico 2W + 1.28" 240x240 round IPS display.

Usage::

    from machine import SPI, Pin
    from lib.gc9a01 import GC9A01, color565

    spi = SPI(0, baudrate=40_000_000, sck=Pin(18), mosi=Pin(19))
    display = GC9A01(spi, cs=Pin(17), dc=Pin(20), rst=Pin(15), bl=Pin(14))
    display.fill(color565(0, 0, 0))          # black background
    display.fill_rect(60, 100, 120, 40, color565(0, 120, 255))
    display.text("Hello!", 80, 115, color565(255, 255, 255))
"""

import time
from micropython import const
import framebuf

# --------------------------------------------------------------------------- #
# Register map (subset used here)                                              #
# --------------------------------------------------------------------------- #
_SWRESET = const(0x01)
_SLPOUT  = const(0x11)
_NORON   = const(0x13)
_INVOFF  = const(0x20)
_INVON   = const(0x21)
_DISPON  = const(0x29)
_CASET   = const(0x2A)
_RASET   = const(0x2B)
_RAMWR   = const(0x2C)
_MADCTL  = const(0x36)
_COLMOD  = const(0x3A)

_MADCTL_MY  = const(0x80)
_MADCTL_MX  = const(0x40)
_MADCTL_MV  = const(0x20)
_MADCTL_BGR = const(0x08)

WIDTH  = const(240)
HEIGHT = const(240)


def color565(r: int, g: int, b: int) -> int:
    """Pack 8-bit (r, g, b) into a 16-bit RGB565 integer."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class GC9A01:
    """Minimal GC9A01 display driver."""

    def __init__(self, spi, *, cs, dc, rst=None, bl=None,
                 width: int = WIDTH, height: int = HEIGHT,
                 rotation: int = 0):
        self._spi  = spi
        self._cs   = cs
        self._dc   = dc
        self._rst  = rst
        self._bl   = bl
        self.width  = width
        self.height = height

        self._cs.init(self._cs.OUT, value=1)
        self._dc.init(self._dc.OUT, value=0)
        if self._rst:
            self._rst.init(self._rst.OUT, value=1)
        if self._bl:
            self._bl.init(self._bl.OUT, value=1)

        self._buf = bytearray(width * height * 2)  # framebuffer (RGB565)
        self._fb  = framebuf.FrameBuffer(self._buf, width, height,
                                         framebuf.RGB565)
        self._init_display(rotation)

    # ----------------------------------------------------------------------- #
    # Low-level helpers                                                        #
    # ----------------------------------------------------------------------- #

    def _write_cmd(self, cmd: int) -> None:
        self._dc(0)
        self._cs(0)
        self._spi.write(bytes([cmd]))
        self._cs(1)

    def _write_data(self, data) -> None:
        self._dc(1)
        self._cs(0)
        self._spi.write(data if isinstance(data, (bytes, bytearray))
                        else bytes([data]))
        self._cs(1)

    def _write_reg(self, cmd: int, *args) -> None:
        self._write_cmd(cmd)
        if args:
            self._write_data(bytes(args))

    def _set_window(self, x0: int, y0: int, x1: int, y1: int) -> None:
        self._write_reg(_CASET, x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)
        self._write_reg(_RASET, y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)
        self._write_cmd(_RAMWR)

    # ----------------------------------------------------------------------- #
    # Initialisation sequence                                                  #
    # ----------------------------------------------------------------------- #

    def _init_display(self, rotation: int = 0) -> None:
        if self._rst:
            self._rst(0)
            time.sleep_ms(10)
            self._rst(1)
            time.sleep_ms(120)

        for cmd, data in _INIT_CMDS:
            self._write_cmd(cmd)
            if data:
                self._write_data(data)
            if cmd == _SLPOUT:
                time.sleep_ms(120)

        # Rotation / colour order
        madctl = {
            0: _MADCTL_MX,
            1: _MADCTL_MV,
            2: _MADCTL_MY,
            3: _MADCTL_MY | _MADCTL_MX | _MADCTL_MV,
        }.get(rotation & 3, _MADCTL_MX)
        self._write_reg(_MADCTL, madctl)
        self._write_reg(_COLMOD, 0x05)  # 16-bit colour
        self._write_cmd(_DISPON)
        time.sleep_ms(20)

    # ----------------------------------------------------------------------- #
    # Drawing API (delegates to framebuf, then flushes)                       #
    # ----------------------------------------------------------------------- #

    def show(self) -> None:
        """Flush the entire framebuffer to the display."""
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._dc(1)
        self._cs(0)
        self._spi.write(self._buf)
        self._cs(1)

    def fill(self, colour: int) -> None:
        self._fb.fill(colour)

    def pixel(self, x: int, y: int, colour: int) -> None:
        self._fb.pixel(x, y, colour)

    def hline(self, x: int, y: int, w: int, colour: int) -> None:
        self._fb.hline(x, y, w, colour)

    def vline(self, x: int, y: int, h: int, colour: int) -> None:
        self._fb.vline(x, y, h, colour)

    def line(self, x0: int, y0: int, x1: int, y1: int, colour: int) -> None:
        self._fb.line(x0, y0, x1, y1, colour)

    def rect(self, x: int, y: int, w: int, h: int, colour: int) -> None:
        self._fb.rect(x, y, w, h, colour)

    def fill_rect(self, x: int, y: int, w: int, h: int, colour: int) -> None:
        self._fb.fill_rect(x, y, w, h, colour)

    def text(self, s: str, x: int, y: int, colour: int) -> None:
        """Draw 8×8 font text (MicroPython built-in font)."""
        self._fb.text(s, x, y, colour)

    def circle(self, x0: int, y0: int, r: int, colour: int) -> None:
        """Draw an unfilled circle using Bresenham's algorithm."""
        x, y, err = r, 0, 0
        while x >= y:
            self._fb.pixel(x0 + x, y0 + y, colour)
            self._fb.pixel(x0 - x, y0 + y, colour)
            self._fb.pixel(x0 + x, y0 - y, colour)
            self._fb.pixel(x0 - x, y0 - y, colour)
            self._fb.pixel(x0 + y, y0 + x, colour)
            self._fb.pixel(x0 - y, y0 + x, colour)
            self._fb.pixel(x0 + y, y0 - x, colour)
            self._fb.pixel(x0 - y, y0 - x, colour)
            y += 1
            err += 2 * y + 1
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

    def fill_circle(self, x0: int, y0: int, r: int, colour: int) -> None:
        """Draw a filled circle."""
        r2 = r * r
        for dy in range(-r, r + 1):
            dx = int((r2 - dy * dy) ** 0.5)
            self._fb.hline(x0 - dx, y0 + dy, 2 * dx + 1, colour)


# --------------------------------------------------------------------------- #
# GC9A01 initialisation command table                                         #
# --------------------------------------------------------------------------- #
_INIT_CMDS = [
    (0xEF, None),
    (0xEB, bytes([0x14])),
    (0xFE, None),
    (0xEF, None),
    (0xEB, bytes([0x14])),
    (0x84, bytes([0x40])),
    (0x85, bytes([0xFF])),
    (0x86, bytes([0xFF])),
    (0x87, bytes([0xFF])),
    (0x88, bytes([0x0A])),
    (0x89, bytes([0x21])),
    (0x8A, bytes([0x00])),
    (0x8B, bytes([0x80])),
    (0x8C, bytes([0x01])),
    (0x8D, bytes([0x01])),
    (0x8E, bytes([0xFF])),
    (0x8F, bytes([0xFF])),
    (0xB6, bytes([0x00, 0x20])),
    (0x3A, bytes([0x05])),
    (0x90, bytes([0x08, 0x08, 0x08, 0x08])),
    (0xBD, bytes([0x06])),
    (0xBC, bytes([0x00])),
    (0xFF, bytes([0x60, 0x01, 0x04])),
    (0xC3, bytes([0x13])),
    (0xC4, bytes([0x13])),
    (0xC9, bytes([0x22])),
    (0xBE, bytes([0x11])),
    (0xE1, bytes([0x10, 0x0E])),
    (0xDF, bytes([0x21, 0x0C, 0x02])),
    (0xF0, bytes([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])),
    (0xF1, bytes([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])),
    (0xF2, bytes([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])),
    (0xF3, bytes([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])),
    (0xED, bytes([0x1B, 0x0B])),
    (0xAE, bytes([0x77])),
    (0xCD, bytes([0x63])),
    (0x70, bytes([0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03])),
    (0xE8, bytes([0x34])),
    (0x62, bytes([0x18, 0x0D, 0x71, 0xED, 0x70, 0x70,
                   0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70])),
    (0x63, bytes([0x18, 0x11, 0x71, 0xF1, 0x70, 0x70,
                   0x18, 0x13, 0x71, 0xF3, 0x70, 0x70])),
    (0x64, bytes([0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07])),
    (0x66, bytes([0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00])),
    (0x67, bytes([0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98])),
    (0x74, bytes([0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00])),
    (0x98, bytes([0x3E, 0x07])),
    (0x35, None),
    (_INVON, None),
    (_SLPOUT, None),
]
