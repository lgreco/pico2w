# pico2w

Leo's projects for the Raspberry Pi Pico 2W.

Repo is a fresh start (currently just this file + README). This file exists
to capture hardware/reference facts up front; as real project work
accumulates here, recurring workflows (build/flash steps, wiring checks,
etc.) should get extracted into a proper `.claude/skills/` skill rather than
re-derived each session.

## Hardware

**MCU:** Raspberry Pi Pico 2W (RP2350, wireless)

No breadboard kit / display / peripherals currently — previous hardware
(52Pi EP-0172 breadboard kit with integrated TFT touchscreen) was returned
due to a malfunctioning display. Hardware setup for this repo is otherwise
unestablished.

## Reference documentation

Sources reviewed for Pico 2 W / RP2350 background. The `datasheets.raspberrypi.org`/
`.com` links below now redirect through `pip.raspberrypi.com` to final hosting on
`pip-assets.raspberrypi.com` — old links still resolve, but expect a redirect chain.

- Adafruit Pico 2 W product page: https://www.adafruit.com/product/6087
- RPi microcontrollers docs hub: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- Pico 2 W datasheet (board-level: pinout, power, wireless, mechanical): https://pip-assets.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w/documents/RP-008304-DS-3-pico-2-w-datasheet.pdf
- Connecting to the Internet with Pico W (networking/Wi-Fi guide, written for Pico W but applies to Pico 2 W's same CYW43439 chip): https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008257-DS-2-connecting-to-the-internet-with-pico-w.pdf
- RP2350 chip datasheet (900+ pages; core architecture, peripherals, power domains, security): https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf
  — note: resisted text extraction via WebFetch/pypdf in this environment (compressed
  PDF streams); if referencing specifics beyond common knowledge, re-fetch/verify
  against the source rather than trusting a prior summary.
- Getting Started with Pico (toolchain setup, build/flash workflow): https://datasheets.raspberrypi.org/pico/getting_started_with_pico.pdf
- Pico Python (MicroPython) SDK reference: https://datasheets.raspberrypi.org/pico/sdk/pico_python_sdk.pdf
- Pico C/C++ SDK reference (HTML, found via docs hub): https://www.raspberrypi.com/documentation/pico-sdk/index.html

## Open questions / not yet established

- What peripherals/hardware this repo will target
- Whether this repo's projects will be C/C++ (Pico SDK) or MicroPython
- Toolchain setup status on this machine (arm-none-eabi-gcc, Pico SDK path,
  picotool) — unverified as of this writing
