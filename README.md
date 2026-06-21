# CyberKey

CyberKey is a local security tool from CyberProff that reduces the risk of unlocked Windows PCs when the user leaves their workstation.

The first MVP is called **CyberKey Slim** and uses an **M1 Coin Beacon** as a personal BLE key.

## Status

Early MVP / testing phase.

The first version focuses on:

- M1 Coin Beacon
- Local BLE scanning on Windows
- RSSI-logging
- Proximity calibration
- Automatic Windows locking later in the test cycle
- No cloud
- No GPS
- No camera
- No automatic unlocking

## Security principle

CyberKey must only lock the machine.

CyberKey must not be used for automatic unlocking, and it does not replace passwords, Windows Hello, or other authentication methods.

BLE proximity is a weak signal suitable for triggering lock actions only.

## Getting started

```bash
git clone https://github.com/cyberproff-no/cyberkey.git
cd cyberkey
cd agent/windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy src\config.example.json src\config.json
python src\cyberkey_scan.py
```

Analyze RSSI log:

```bash
python src\analyze_rssi.py
```

## MVP goals

The first phase collects data and does not make security decisions.

The goal is to determine:

- how M1 behaves on Windows
- which BLE identifiers are stable
- how RSSI varies at 0.5 m, 1.5 m, and 3 m
- how often the signal drops during normal use
- which thresholds can be used later in the proximity engine

## Not in MVP

- automatic unlocking
- centralized administration
- gateway support
- mobile app
- web dashboard
- employee tracking
- H1 button support
- H3 badge mode

## License

Program code is licensed under GPL-3.0-or-later.

The CyberKey and CyberProff names, logos, and brand are not licensed for commercial use without written permission.
