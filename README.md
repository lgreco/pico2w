# pico2w

Simple experiments on a **Raspberry Pi Pico 2W** using the
[52PI.com breadboard kit](https://wiki.52pi.com/) with a capacitive touch screen.

---

## Hardware

| Component | Details |
|-----------|---------|
| MCU board | Raspberry Pi Pico 2W (RP2350, dual-core Cortex-M33 + 2.4 GHz Wi-Fi/BT) |
| Kit | 52PI breadboard expansion kit |
| Display | 1.28″ round IPS LCD, 240 × 240, GC9A01 driver (SPI) |
| Touch | CST816S capacitive touch controller (I²C, address `0x15`) |
| Interface | SPI (display) + I²C (touch) |

### Default Pin Mapping

```
Display (SPI0)
  SCK  → GP18
  MOSI → GP19
  CS   → GP17
  DC   → GP20
  RST  → GP15
  BL   → GP14 (backlight, PWM)

Touch (I2C0)
  SDA  → GP4
  SCL  → GP5
  INT  → GP21 (interrupt, active-low)
  RST  → GP22
```

> Adjust `PIN_*` constants in each script if your wiring differs.

---

## Requirements

* [MicroPython for RP2350](https://micropython.org/download/RPI_PICO2_W/) flashed onto the Pico 2W
* [Thonny IDE](https://thonny.org/) **or** [mpremote](https://pypi.org/project/mpremote/) for uploading files

---

## Repository Layout

```
pico2w/
├── main.py               # Interactive touch-draw demo (runs on boot)
├── blink.py              # Standalone onboard-LED blink example
├── examples/
│   ├── display_basic.py  # Initialise display and draw shapes / text
│   ├── touch_basic.py    # Poll CST816S and print touch coordinates
│   └── touch_draw.py     # Draw on the LCD with your finger
└── lib/
    ├── gc9a01.py         # GC9A01 display driver (MicroPython, SPI)
    └── cst816s.py        # CST816S capacitive touch driver (MicroPython, I²C)
```

---

## Quick Start

1. Flash MicroPython onto the Pico 2W.
2. Copy the `lib/` directory to the root of the Pico's filesystem.
3. Copy whichever example you want to run (or `main.py`) to the root.
4. Reset the board — the script runs automatically if named `main.py`.

### Using mpremote

```bash
# install mpremote
pip install mpremote

# copy drivers
mpremote cp lib/gc9a01.py  :lib/gc9a01.py
mpremote cp lib/cst816s.py :lib/cst816s.py

# run an example directly (without copying)
mpremote run examples/display_basic.py
```

---

## Examples

### Blink (`blink.py`)
Blinks the onboard LED. Good first smoke-test after flashing MicroPython.

### Display Basic (`examples/display_basic.py`)
Draws filled rectangles, circles, and a text greeting on the round LCD.

### Touch Basic (`examples/touch_basic.py`)
Reads touch events from the CST816S and prints `(x, y, gesture)` to the
REPL.

### Touch Draw (`examples/touch_draw.py`)
Full paint demo: drag your finger on the screen to draw coloured pixels.

### Main Demo (`main.py`)
Combines the display and touch demos into an interactive launcher that runs
at startup.

---

## License

MIT — see [LICENSE](LICENSE) file (add one if distributing).
