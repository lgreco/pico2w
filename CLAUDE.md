# pico2w

Leo's projects for the Raspberry Pi Pico 2W, mounted on the **52Pi EP-0172
"Pico Breadboard Kit Plus"** — a breadboard base with an integrated 3.5"
capacitive touchscreen plus assorted I/O (joystick, RGB LED, buzzer, buttons,
LEDs).

Repo is a fresh start (currently just this file + README). This file exists
to capture hardware/reference facts up front; as real project work
accumulates here, recurring workflows (build/flash steps, display init
boilerplate, wiring checks, etc.) should get extracted into a proper
`.claude/skills/` skill rather than re-derived each session.

## Hardware

**MCU:** Raspberry Pi Pico 2W (RP2350, wireless)

**Breadboard kit:** 52Pi EP-0172 ("Pico Breadboard Kit Plus")
- Product page: https://wiki.52pi.com/index.php?title=EP-0172
- Reference firmware/demo repo: https://github.com/geeekpi/pico_breakboard_kit
  (note: actual org/repo is `geeekpi/pico_breakboard_kit`, *not*
  `geekpi/pico_breadboard_kit` — easy typo, both "geeekpi" (triple e) and
  "breakboard" differ from the intuitive spelling)
  - `master` branch: original Pico (RP2040) target
  - `pico2` branch: adapted for Pico 2 family (RP2350) — this is the
    relevant branch for this repo's target board
  - No LICENSE file in that repo — treat any copied code as reference/study
    material rather than something to vendor wholesale without checking
    with Leo first.

### Display

- 3.5" capacitive touchscreen, 320×480
- Display driver IC: ST7796SU1 (may vary by batch)
- Display bus: SPI
- Touch bus: I2C
- Logic voltage: 3.3V

### Pinout (per 52Pi wiki + reference repo)

| Function        | Pico GPIO |
|------------------|-----------|
| Display CLK      | GP2       |
| Display DIN(MOSI)| GP3       |
| Display CS       | GP5       |
| Display DC       | GP6       |
| Display RST      | GP7       |
| Touch SDA        | GP8       |
| Touch SCL        | GP9       |
| RGB LED          | GP12      |
| Buzzer           | GP13      |
| Button 2 (BTN2)  | GP14      |
| Button 1 (BTN1)  | GP15      |
| LED              | GP16      |
| LED              | GP17      |
| Joystick X       | ADC0      |
| Joystick Y       | ADC1      |

Extra LED rows also reference 3V3/5V power pins directly (not GPIO-driven).

Double-check this table against the physical board / silkscreen before
wiring anything new — it's transcribed from vendor docs, not verified against
this specific unit yet.

## Software stack (per reference repo)

- Raspberry Pi Pico SDK (C/C++)
- LVGL (graphics/UI library) — driven via `lv_port_disp.*` / `lv_port_indev.*`
- FreeRTOS kernel
- Build via CMake (≥3.13) + arm-none-eabi-gcc; clone reference repo with
  `--recursive` (submodules under `components/`); flash by copying the
  built `.uf2` to the Pico's USB mass-storage device (BOOTSEL mode)
- Vendor notes MicroPython/LVGL is not viable given the 264KB RAM budget —
  worth keeping in mind if considering MicroPython for this repo's own code

## Open questions / not yet established

- Whether this repo's projects will be C/C++ (Pico SDK) or MicroPython
- Whether we're forking/vendoring the `pico2` branch of the reference repo
  or writing from scratch
- Toolchain setup status on this machine (arm-none-eabi-gcc, Pico SDK path,
  picotool) — unverified as of this writing
