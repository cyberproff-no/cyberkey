# CyberKey Proximity Engine Design

## Purpose

`proximity.py` evaluates BLE proximity using RSSI data from the target beacon.

The module must:

* receive raw RSSI measurements from the BLE scanner
* smooth signal noise using a moving average
* maintain a deterministic proximity state machine
* detect when the beacon stops transmitting packets
* provide decision data to a later policy engine

The module must not:

* lock Windows directly
* unlock Windows
* authenticate users
* use cloud services, GPS, cameras, or employee tracking

## Architecture

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

Responsibilities:

* `cyberkey_scan.py`: detects BLE advertisements and forwards RSSI data
* `proximity.py`: evaluates signal state and emits an optional lock request
* `policy.py`: evaluates test mode, cooldowns, idle time, and other rules
* `locker.py`: performs the actual Windows lock operation when policy permits it

## Security Model

BLE proximity is a weak signal.

It may only be used for restrictive actions, such as locking Windows.

It must never be used for:

* unlocking
* authentication
* identity verification
* standalone access control

## States

| State       | Meaning                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------- |
| `UNKNOWN`   | The beacon has not been observed yet, or it has just returned and new samples are being collected |
| `NEAR`      | Stable and strong RSSI signal                                                                     |
| `UNCERTAIN` | Signal is in the gray zone between near and away                                                  |
| `AWAY`      | Stable weak RSSI signal                                                                           |
| `LOST`      | No BLE packets have been received within the configured timeout                                   |

The initial state is always `UNKNOWN`.

CyberKey must never request a lock before the target beacon has actually been observed.

## RSSI Smoothing

RSSI naturally fluctuates in BLE environments.

The proximity engine therefore uses a sliding window with a moving average.

Example configuration:

```
window_size = 5
min_samples = 3
```

Before at least `min_samples` valid measurements have been received, the state remains `UNKNOWN`.

## RSSI Thresholds

Example thresholds:

```
rssi_near = -65
rssi_away = -80
```

Rules:

```
average_rssi >= rssi_near
    → NEAR

rssi_away < average_rssi < rssi_near
    → UNCERTAIN

average_rssi <= rssi_away
    → AWAY
```

These values must later be calibrated using RSSI logs from the actual M1 Coin Beacon.

## Timeout Model

CyberKey uses separate timing thresholds:

```
lost_after_seconds
lock_after_away_seconds
lock_after_lost_seconds
```

Their roles are:

* `lost_after_seconds`: when the beacon is considered lost
* `lock_after_away_seconds`: how long `AWAY` must persist before a lock request
* `lock_after_lost_seconds`: how long `LOST` must persist before a lock request

The same timeout must not be used both for the transition to `LOST` and for the actual lock request.

## Lock Latch

When the proximity engine emits a lock request, it sets:

```
lock_requested = True
```

After that, `should_lock()` must not return `True` repeatedly.

The latch is reset only when the beacon returns and reaches a stable `NEAR` state again.

This prevents repeated lock attempts.

## Time Handling

Internal timeout logic uses `time.monotonic()`.

This is used instead of `time.time()` because the monotonic clock is not affected by:

* manual system time changes
* NTP synchronization
* daylight saving time
* operating system clock adjustments

## Test Strategy

`agent/windows/tests/test_proximity.py` uses synthetic RSSI values and synthetic timestamps.

The tests cover:

1. Beacon never observed → no lock request
2. Stable strong RSSI values → `NEAR`
3. Noise around the threshold → `UNCERTAIN`
4. Weak RSSI values → `AWAY`
5. Missing packets → `LOST`
6. `AWAY` long enough → one lock request
7. `LOST` long enough → one lock request
8. Beacon returns → lock latch resets
9. Lock requests cannot repeat without a new return and departure cycle

## Future Work

Once the proximity engine is stable, `policy.py` can be implemented on top of it.

The policy engine will later handle:

* `test_mode`
* cooldown after locking
* keyboard and mouse idle time
* whether the agent is enabled
* a possible presentation mode
* calls to `locker.py`

`proximity.py` must never call `LockWorkStation()` directly.
