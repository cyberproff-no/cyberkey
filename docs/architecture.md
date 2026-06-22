# CyberKey Architecture

## Current Status
CyberKey is in an early MVP and testing phase.

The physical M1 Coin Beacon is not yet available for validation.

The Windows BLE scanner collects local BLE and RSSI data. The proximity and policy engines are implemented and unit-tested with synthetic inputs.

The proximity and policy engines are not yet connected to the scanner or to Windows locking. Automatic Windows locking is not enabled in the current end-to-end agent.

## Current Runtime Path

```
cyberkey_scan.py
    ↓
Local RSSI logging
    ↓
analyze_rssi.py
```
This runtime path is used for BLE discovery, local logging, and later RSSI calibration.

## Implemented Components Not Yet Runtime-Connected

```
proximity.py
    ↓
policy.py
    ↓
locker.py
```
These components are implemented as separate modules but are not yet connected to the scanner or to each other in the running agent.

## Planned Integration Path

```
cyberkey_scan.py
    ↓
proximity.py
    ↓
policy.py
    ↓
locker.py
    ↓
Windows LockWorkStation
```
This integration path remains disabled until M1 hardware validation, RSSI calibration, and end-to-end testing have been completed.

## Windows Agent Responsibility Separation

- `cyberkey_scan.py` receives BLE advertisements and records raw RSSI observations locally.
- `proximity.py` evaluates RSSI data and provides proximity state plus lock-request decision data only.
- `policy.py` applies operational rules such as test mode, cooldown, idle checks, disabled mode, and presentation mode.
- `locker.py` is the only component allowed to call the Windows locking API.

## Security Invariants

- BLE proximity is a weak signal.
- BLE may only contribute to restrictive actions such as locking Windows.
- BLE must never be used for unlocking, authentication, identity verification, or standalone access control.
- `proximity.py` must never call `LockWorkStation()` directly.
- `policy.py` must never call `LockWorkStation()` directly.
- Automatic Windows locking remains disabled until controlled runtime integration and hardware validation are complete.
