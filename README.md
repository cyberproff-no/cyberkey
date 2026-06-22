# CyberKey

CyberKey is a local security tool from CyberProff that reduces the risk of unlocked Windows PCs when the user leaves their workstation.

The first MVP is called **CyberKey Slim** and uses an **M1 Coin Beacon** as a personal BLE key.

## Status

Prototype / testing phase.

The Windows scanner collects local BLE and RSSI data. The standalone proximity and policy engines are implemented and unit-tested.

The proximity engine produces proximity states and one-shot lock-request decisions. The policy engine applies test-mode, idle-time, cooldown, and presentation-mode rules. Neither component is yet connected to the scanner or to Windows locking.

Automatic locking is not enabled in the current end-to-end agent.

Hardware status:

The physical M1 Coin Beacon is not yet available for validation.

Current proximity and policy behavior has been verified with synthetic tests. Nearby BLE discovery has been verified separately. M1-specific discovery, RSSI calibration, identifier validation, and end-to-end testing remain pending until the hardware is available.

Current focus:

- M1 Coin Beacon
- Local BLE scanning on Windows
- Local RSSI logging and calibration
- Proximity state evaluation
- Synthetic unit tests for proximity behavior
- No cloud
- No GPS
- No camera
- No automatic unlocking

## Security principle

CyberKey must only lock the machine.

CyberKey must not be used for automatic unlocking, and it does not replace passwords, Windows Hello, or other authentication methods.

BLE proximity is a weak signal suitable for triggering lock actions only.

## Getting started

Run the following in PowerShell:

```powershell
git clone https://github.com/cyberproff-no/cyberkey.git
Set-Location .\cyberkey\agent\windows

python -m venv .venv
\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Copy-Item src\config.example.json src\config.json

python src\cyberkey_scan.py
```

The default configuration runs in discovery mode and writes local RSSI logs. Edit `src\config.json` before testing against a specific beacon.

Analyze RSSI log:

```powershell
python src\analyze_rssi.py
```

## MVP goals

The MVP currently has two separate goals:

1. Collect local BLE and RSSI data from the M1 Coin Beacon.
2. Validate the proximity and policy engines with calibrated RSSI values and synthetic tests.

The current scanner does not trigger policy decisions or Windows locking.

The next integration phase will connect scanner observations to proximity and policy evaluation while Windows locking remains disabled by default.

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
