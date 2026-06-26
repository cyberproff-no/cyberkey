# CyberKey
> Status: Prototype — synthetic dry-run integration complete.
> M1 hardware validation pending.
> Automatic Windows locking is disabled.

CyberKey is a local security tool from CyberProff that reduces the risk of unlocked Windows PCs when a user leaves their workstation.

The first MVP is called **CyberKey Slim** and is designed to evaluate an **M1 Coin Beacon** as a local BLE proximity signal.

## Status
Prototype and testing phase.

CyberKey currently has two separate local paths:

```
cyberkey_scan.py
	-> local RSSI logging
	-> analyze_rssi.py
```
This path is used for BLE discovery, local data collection, and later RSSI calibration.

```
synthetic RSSI event or timeout tick
	-> DryRunAgent
	-> ProximityEngine
	-> PolicyEngine
	-> NONE or WOULD_LOCK
```
The dry-run path uses deterministic synthetic input and forces `test_mode=True`.

The current end-to-end agent does not use live BLE scanning, does not import `locker.py`, does not call Windows APIs, and does not lock Windows.

Automatic Windows locking remains disabled.

Hardware status:

The physical M1 Coin Beacon is not yet available for validation.

M1-specific discovery, identifier validation, RSSI calibration, packet-loss measurement, and hardware end-to-end validation remain pending until the beacon is available.

## Current Focus

- M1 Coin Beacon hardware validation
- Local BLE discovery on Windows
- Local RSSI logging and calibration
- Proximity state evaluation
- Synthetic dry-run testing
- Local-only operation
- No cloud
- No GPS
- No camera
- No employee tracking
- No automatic unlocking

## Security Principle
BLE proximity is a weak signal.

CyberKey may use BLE proximity only as one input toward a restrictive action such as locking a Windows session.

CyberKey must not use BLE proximity for:

- Automatic unlocking
- Authentication
- Identity verification
- Standalone access control

CyberKey does not replace passwords, Windows Hello, or other authentication methods.

## Getting Started
Run the following in PowerShell:

```
git clone https://github.com/cyberproff-no/cyberkey.git
Set-Location .\cyberkey\agent\windows

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Copy-Item src\config.example.json src\config.json

python src\cyberkey_scan.py
```
The default configuration runs in discovery mode and writes local RSSI logs. Edit `src\config.json` before testing against a specific beacon.

Analyze an RSSI log:

```
python src\analyze_rssi.py
```
Run the synthetic test suite:

```
python -m unittest discover -s tests -p "test_*.py" -v
```

## MVP Goals
The MVP currently has two separate goals:

1. Collect local BLE and RSSI data from the M1 Coin Beacon.
2. Validate proximity and policy behavior with deterministic synthetic tests.

The scanner does not trigger policy decisions or Windows locking.

A future live adapter may pass validated local beacon RSSI samples into the existing dry-run interface. That future work remains `test_mode=True` and `WOULD_LOCK` only until separate hardware validation and safety review are complete.

## Not in MVP

- Automatic Windows locking
- Automatic unlocking
- Authentication or identity verification
- Standalone access control
- Centralized administration
- Gateway support
- Mobile app
- Web dashboard
- Employee tracking
- H1 button support
- H3 badge mode

## License, Hardware and Trademarks

### Software license

CyberKey source code is licensed under the
GNU General Public License v3.0 or later (`GPL-3.0-or-later`).

This means you may inspect, use, modify, and redistribute the software,
including commercially, provided that redistributed derivative works are
made available under the same GPL-compatible terms and include the
corresponding source code.

See [LICENSE](LICENSE) for the complete license text.

### Third-party hardware

CyberKey is software that can work with compatible third-party Bluetooth
Low Energy beacons.

CyberProff.no does not manufacture, supply, certify, warrant, or license
the beacon hardware itself. Hardware compatibility may vary depending on
the beacon model, firmware, configuration, Bluetooth adapter, operating
system, physical environment, and radio conditions.

The initial CyberKey Slim prototype is designed around the M1 Coin Beacon,
but this does not imply endorsement, partnership, sponsorship, or
certification by the beacon manufacturer.

### Security notice

CyberKey uses Bluetooth proximity signals as one input to Windows locking
behavior. Bluetooth signal conditions can change due to distance,
interference, walls, battery level, device placement, and environmental
factors.

CyberKey is not a replacement for strong authentication, disk encryption,
endpoint protection, device management, or security policy enforcement.

Test your own setup before relying on CyberKey in security-sensitive or
business-critical environments.

### Trademarks

CyberKey, CyberKey Slim, CyberProff, CyberProff.no, associated logos,
product names, and visual identity are not licensed under GPLv3.

Forks and derivative works must use their own name and branding and must
not imply endorsement, certification, sponsorship, or affiliation with
CyberProff.no.

See [TRADEMARKS.md](TRADEMARKS.md) for the complete trademark policy.
