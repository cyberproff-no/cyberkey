# CyberKey Architecture

CyberKey MVP consists of a simple local Windows agent.

```text
M1 Coin Beacon
    ↓
BLE scanner
    ↓
RSSI logging
    ↓
Analysis
    ↓
Proximity engine later
    ↓
Windows lock later
```

## First phase

The first phase implements only BLE discovery, raw logging, and basic RSSI analysis.

No locking logic should be activated until enough test data exists.

## Windows Agent Responsibility Separation

- `cyberkey_scan.py` receives BLE advertisements and forwards raw RSSI observations.
- `proximity.py` evaluates RSSI data and provides proximity state plus lock-request decision data only.
- `policy.py` will later apply operational rules such as test mode, cooldown, idle checks, and presentation mode.
- `locker.py` is the only component allowed to call the Windows locking API.

### Security invariants

- `proximity.py` must never call `LockWorkStation()` directly.
- BLE proximity is a weak signal and may only trigger restrictive actions such as locking.
- BLE must never be used for unlocking, authentication, identity verification, or standalone access control.
