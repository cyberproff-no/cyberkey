# Dry-Run Integration Design

## Status
This document describes the safe synthetic integration path for CyberKey before physical M1 Coin Beacon hardware is available.

The current integration is intentionally limited to deterministic synthetic input and policy output. It does not scan for BLE devices and does not perform Windows locking.

## Purpose
The dry-run path validates the intended decision flow:

```
synthetic RSSI event or timeout tick
    -> ProximityEngine
    -> PolicyEngine
    -> AgentResult with NONE or WOULD_LOCK
```
Its purpose is to validate proximity behavior, policy gating, latches, and future integration boundaries without interacting with Windows session state.

## Components

### `agent/windows/src/proximity.py`
`ProximityEngine` receives RSSI samples and timeout ticks.

It is responsible for:

- RSSI moving-average handling
- Proximity state transitions
- AWAY and LOST timeout behavior
- One-shot logical lock requests
- Rearming its lock latch after a stable NEAR return

It does not call Windows APIs or perform locking.

### `agent/windows/src/policy.py`
`PolicyEngine` receives a logical lock request from the proximity engine.

It is responsible for:

- Enabled and disabled policy state
- Presentation-mode suppression
- Idle-time gating
- Cooldown handling
- Policy request latching
- Returning `NONE`, `WOULD_LOCK`, or `LOCK_ALLOWED`

It does not import `locker.py` or call Windows APIs.

### `agent/windows/src/agent.py`
`DryRunAgent` is the safe orchestration layer.

It accepts only caller-supplied synthetic input through:

- `process_rssi(rssi, idle_seconds, now)`
- `process_timeout(idle_seconds, now)`

For each event, it:

1. Updates or checks the proximity engine.
2. Evaluates whether proximity has issued a logical lock request.
3. Passes the current request state to the policy engine.
4. Returns an `AgentResult`.

`DryRunAgent` does not perform logging, device discovery, locking, authentication, identity verification, or access control.

## Security Boundaries
The dry-run integration must preserve the following rules:

- No live BLE scanner integration.
- No import of `locker.py`.
- No `LockWorkStation()` call.
- No Windows API calls.
- No unlock capability.
- No authentication or identity verification.
- No standalone access-control decision.
- No cloud service, telemetry, GPS, camera, or employee tracking.
- BLE proximity remains a weak signal that may only contribute to restrictive actions.

## Forced Test Mode
`DryRunAgent` always forces:

```
test_mode=True
```
A caller that explicitly provides `test_mode=False` receives a `ValueError`.

This guarantees that the dry-run path can return `WOULD_LOCK`, but cannot return `LOCK_ALLOWED`.

## Deterministic Time Model
All synthetic agent calls require an explicit `now` value.

The agent validates that timestamps are:

- Numeric
- Non-negative
- Non-decreasing across calls

This makes tests reproducible and prevents dependence on wall-clock time.

`idle_seconds` is also caller-supplied synthetic input. A future live integration may provide idle time from a dedicated local Windows idle-time adapter, but that adapter is outside the current scope.

## Request and Latch Behavior
The proximity engine creates one logical lock request per departure cycle.

A request may be blocked by policy because of:

- Insufficient idle time
- Active cooldown
- Disabled policy
- Presentation mode

When idle time or cooldown blocks a request, the request remains available for later policy evaluation.

After a successful `WOULD_LOCK` result, the policy latch prevents repeated `WOULD_LOCK` results for the same proximity request.

A stable NEAR return clears the proximity lock latch. The following no-request policy evaluation clears the policy request latch. A later departure may then create a new logical lock request.

This behavior prevents repeated output during one absence while allowing a future departure cycle after beacon return.

## Synthetic Test Coverage
`agent/windows/tests/test_agent.py` provides end-to-end tests for:

1. Strong RSSI leading to NEAR with no action.
2. Weak RSSI held long enough to reach AWAY and produce `WOULD_LOCK`.
3. Missing packets reaching LOST and producing `WOULD_LOCK`.
4. Idle threshold gating until sufficient idle time exists.
5. Cooldown blocking a later departure request until expiry.
6. Proximity and policy latches preventing repeated `WOULD_LOCK` output.
7. Stable NEAR return rearming a future departure cycle.

The tests use deterministic timestamps and do not require BLE hardware, Windows APIs, or `locker.py`.

## Explicitly Excluded from This Phase
The following work remains out of scope:

- Live BLE scanning
- M1 Coin Beacon discovery
- Beacon identifier validation
- RSSI calibration using physical hardware
- Windows idle-time collection
- Runtime file logging
- Windows locking
- Unlock behavior
- Authentication or access-control behavior

## Hardware Integration Direction
When M1 Coin Beacon hardware becomes available, a separate adapter should validate target advertisements and pass accepted RSSI samples into the existing agent interface.

The future adapter should use:

```
validated beacon RSSI sample
    -> DryRunAgent.process_rssi(...)
```
It must not modify proximity or policy state directly.

Hardware validation must continue in `test_mode=True` and `WOULD_LOCK` mode before any future discussion of real Windows locking.
