# CyberKey Architecture

## Current Status
CyberKey is in an early MVP and testing phase.

The physical M1 Coin Beacon is not yet available for validation.

Automatic Windows locking is disabled.

## Current Local Paths
CyberKey currently has two separate local paths.

### BLE Discovery and Data Collection

```
cyberkey_scan.py
    -> local RSSI logging
    -> analyze_rssi.py
```
This path is used for local BLE discovery, raw RSSI collection, and later hardware calibration.

It does not call `proximity.py`, `policy.py`, `agent.py`, or `locker.py`.

### Synthetic Dry-Run Evaluation

```
synthetic RSSI event or timeout tick
    -> DryRunAgent
    -> ProximityEngine
    -> PolicyEngine
    -> NONE or WOULD_LOCK
```
This path uses deterministic caller-supplied input.

`DryRunAgent` forces `test_mode=True`.

It does not use live BLE scanning, does not import `locker.py`, does not call Windows APIs, and does not lock Windows.

## Component Responsibilities

### `cyberkey_scan.py`

- Receives BLE advertisements.
- Records local RSSI observations.
- Supports discovery and later local calibration.
- Is not connected to the dry-run agent.

### `analyze_rssi.py`

- Analyzes locally collected RSSI logs.
- Supports later calibration review.
- Does not make proximity or policy decisions.

### `agent.py`

- Accepts synthetic RSSI samples and timeout ticks.
- Orchestrates `ProximityEngine` and `PolicyEngine`.
- Returns decision data through `AgentResult`.
- Forces `test_mode=True`.
- Does not perform BLE discovery, locking, authentication, or access control.

### `proximity.py`

- Smooths RSSI observations.
- Maintains proximity states.
- Produces one-shot logical lock requests.
- Does not call Windows APIs.

### `policy.py`

- Applies enabled state, presentation mode, idle threshold, and cooldown rules.
- Returns `NONE`, `WOULD_LOCK`, or `LOCK_ALLOWED`.
- Does not call Windows APIs.
- Returns `WOULD_LOCK` in the current dry-run path because `test_mode=True`.

### `locker.py`

- Contains the isolated Windows lock helper.
- Is not connected to the current runtime path.
- Must remain unavailable to proximity and policy modules.

## Future Hardware Validation Direction
After M1 hardware validation, a separate local adapter may be considered.

```
validated local M1 advertisement
    -> accepted RSSI sample
    -> DryRunAgent.process_rssi(...)
    -> WOULD_LOCK logging only
```
The future adapter must validate local advertisement fields before forwarding an RSSI sample.

It must not modify `ProximityEngine` or `PolicyEngine` state directly.

Hardware integration must remain in `test_mode=True` and `WOULD_LOCK` mode until a separate safety review is completed.

## Disabled Future Locking Boundary
A later locking phase, if explicitly approved, would remain separate:

```
validated local signal
    -> proximity decision
    -> policy decision
    -> explicit lock integration
    -> Windows LockWorkStation
```
This path is not implemented or enabled in the current runtime.

## Security Invariants

- BLE proximity is a weak signal.
- BLE may only contribute to restrictive actions such as locking Windows.
- BLE must never be used for automatic unlocking.
- BLE must never be used for authentication, identity verification, or standalone access control.
- `proximity.py` must never call `LockWorkStation()` directly.
- `policy.py` must never call `LockWorkStation()` directly.
- `DryRunAgent` must not import `locker.py`.
- No cloud, GPS, camera, telemetry, or employee tracking is part of the MVP.
- Automatic Windows locking remains disabled until controlled runtime integration and hardware validation are complete.
