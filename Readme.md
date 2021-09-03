# RasPad Auto Rotator

A simple script for auto rotating RasPad display with Accel SHIM

## Compatiable

Currently supports:

- Raspberry Pi OS
- Twister OS
- Ubuntu Desktop 21.04

## Install

```bash
git clone https://github.com/raspad-tablet/raspad-auto-rotator
cd raspad-auto-rotator
sudo python3 install.py
```

## Usage

After installation, it might prompt to reboot, if so, reboot it, and the auto rotation will work. If no reboot prompt. the auto rotation also works right after installation finished.

## Calibration

After first install, some angle may not trigger the auto rotation, Try filp to the opposet side for about a second, and filp back, it will automatically calibrate it self. Or do a standard calibration move, rotate the RasPad in all 3 axis for 720 degree slowly, it will also calibrate itself.

Sometimes, no matter how you rotate and calibrate it, it just don't work in some angle, if that happened, try to reset the calibration with command:

```bash
raspad-auto-rotate reset
```

After this command runs, calibrateion resets and auto rotator restarts itself. Now try recalibrate it as mention above.
