# CyberKey Policy Engine Design

## Purpose

`policy.py` applies operational safety rules to a proximity lock request before any lock action may be allowed.

The policy engine sits between `proximity.py` and `locker.py`.

It must:

- receive the current lock-request state from the proximity engine
- enforce test mode, idle-time, and cooldown rules
- support disabled and presentation modes
- return a decision that later integration code can act on
- remain deterministic and easy to test

It must not:

- unlock Windows
- authenticate users
- verify identity
- read keyboard or mouse activity directly
- call `LockWorkStation()` directly
- import or depend on Windows APIs

## Architecture

	cyberkey_scan.py
		↓
	proximity.py
		↓
	policy.py
		↓
	locker.py
		↓
	Windows LockWorkStation

Responsibilities:

- `cyberkey_scan.py` receives BLE advertisements and forwards raw RSSI observations.
- `proximity.py` maintains the BLE proximity state machine and exposes the current logical lock-request state.
- `policy.py` determines whether that request may become a policy action.
- `locker.py` will later be the only component allowed to call the Windows locking API.

## Security Model

BLE proximity is a weak signal.

It may only contribute to restrictive actions such as locking Windows.

It must never be used for:

- unlocking
- authentication
- identity verification
- standalone access control

`policy.py` does not decide whether a user is trusted. It only decides whether a restrictive lock action is currently allowed by operational policy.

## Input Contract

The policy engine receives:

- `lock_requested`
- `lock_reason`
- `idle_seconds`
- `now`

`lock_requested` must represent the current logical request state from `proximity.py`, not only the one-time return value from `should_lock()`.

This is important because policy may need to wait for the idle threshold or cooldown before acting on the same proximity request.

Future integration should therefore use the persistent proximity request state, for example:

	lock_requested = proximity.lock_requested
	lock_reason = proximity.lock_reason

## Policy Actions

The policy engine can return one of these actions:

| Action | Meaning |
|---|---|
| `NONE` | No lock action is allowed or required |
| `WOULD_LOCK` | Test mode is enabled; an action would be logged but Windows must not be locked |
| `LOCK_ALLOWED` | Policy permits a later integration layer to call `locker.py` |

`LOCK_ALLOWED` does not itself lock Windows.

## Operational Rules

### Test Mode

When `test_mode` is enabled, a valid lock request returns:

	WOULD_LOCK

This allows safe testing without calling the Windows lock API.

### Idle Threshold

The caller provides `idle_seconds` from a later idle-time provider.

A lock request remains blocked until:

	idle_seconds >= min_idle_seconds

The policy engine does not access keyboard or mouse APIs directly.

### Cooldown

After a policy action is produced, the engine records the action time.

New lock requests are blocked until:

	cooldown_seconds

has elapsed.

This prevents repeated policy actions in a short period.

### Disabled Policy

When policy is disabled:

	enabled = False

incoming lock requests are discarded for the current request cycle.

### Presentation Mode

When presentation mode is active:

	presentation_mode = True

incoming lock requests are discarded for the current request cycle.

This avoids disruptive locking during a presentation or other future approved mode.

## Request Handling

The policy engine has its own request-handling latch.

A proximity request may produce only one policy action.

After an action is produced, the same request returns:

	NONE
	reason = request_already_handled

The policy latch resets only after the proximity request is no longer active.

This means that a new action requires a new proximity request cycle.

## Time Handling

Internal cooldown timing uses:

	time.monotonic()

This avoids errors caused by system clock changes, NTP synchronization, daylight saving changes, or manual clock adjustments.

## Test Strategy

`agent/windows/tests/test_policy.py` uses synthetic inputs and synthetic timestamps.

The tests cover:

1. No proximity lock request returns `NONE`
2. Test mode returns `WOULD_LOCK`
3. Non-test mode returns `LOCK_ALLOWED`
4. The same request is handled only once
5. Idle threshold blocks until the requirement is met
6. Disabled policy discards the request
7. Presentation mode discards the request
8. Cooldown blocks a new request until it expires
9. Negative idle time is rejected
10. Snapshot data reports current policy state

## Future Work

Future integration work may add:

- a Windows idle-time provider for keyboard and mouse inactivity
- controlled calls from a policy integration layer to `locker.py`
- explicit logging of `WOULD_LOCK` events
- configuration loading from `config.json`
- presentation-mode controls
- process supervision and agent lifecycle handling

`policy.py` must remain separate from direct Windows locking code.
