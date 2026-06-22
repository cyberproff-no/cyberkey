"""
CyberKey Proximity Engine

Purpose:
- Receive raw RSSI values from the BLE scanner.
- Smooth RSSI noise using a moving average.
- Maintain a deterministic proximity state machine.
- Provide state and lock-request decisions only.

Security rule:
This module must never unlock Windows, authenticate users,
or call the Windows lock API directly.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any


class ProximityState:
    UNKNOWN = "UNKNOWN"
    NEAR = "NEAR"
    UNCERTAIN = "UNCERTAIN"
    AWAY = "AWAY"
    LOST = "LOST"


class ProximityEngine:
    """
    Pure proximity state machine.

    The caller is responsible for:
    - Passing RSSI values from the BLE scanner to update().
    - Calling check_timeouts() regularly.
    - Passing a lock request to policy.py later.

    This class never performs Windows locking itself.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}

        self.rssi_near = int(config.get("rssi_near", -65))
        self.rssi_away = int(config.get("rssi_away", -80))

        self.window_size = int(config.get("window_size", 5))
        self.min_samples = int(config.get("min_samples", 3))

        self.lost_after_seconds = float(
            config.get("lost_after_seconds", 5)
        )
        self.lock_after_away_seconds = float(
            config.get("lock_after_away_seconds", 10)
        )
        self.lock_after_lost_seconds = float(
            config.get("lock_after_lost_seconds", 5)
        )

        self._validate_config()

        self.rssi_window: deque[int] = deque(maxlen=self.window_size)

        self.current_state = ProximityState.UNKNOWN
        self.state_entered_at = time.monotonic()
        self.last_seen_at: float | None = None

        self.has_seen_target = False
        self.lock_requested = False
        self.lock_reason: str | None = None

    def _validate_config(self) -> None:
        if self.rssi_near <= self.rssi_away:
            raise ValueError(
                "rssi_near must be greater than rssi_away "
                "(for example -65 > -80)."
            )

        if self.window_size < 1:
            raise ValueError("window_size must be at least 1.")

        if self.min_samples < 1:
            raise ValueError("min_samples must be at least 1.")

        if self.min_samples > self.window_size:
            raise ValueError(
                "min_samples cannot be greater than window_size."
            )

        if self.lost_after_seconds <= 0:
            raise ValueError("lost_after_seconds must be greater than 0.")

        if self.lock_after_away_seconds < 0:
            raise ValueError(
                "lock_after_away_seconds cannot be negative."
            )

        if self.lock_after_lost_seconds < 0:
            raise ValueError(
                "lock_after_lost_seconds cannot be negative."
            )

    def update(self, rssi: int, now: float | None = None) -> str:
        """
        Register one RSSI sample from the target beacon.

        The optional now parameter exists for deterministic unit tests.
        Production code should normally omit it.
        """
        now = time.monotonic() if now is None else now

        returning_from_lost = (
            self.has_seen_target
            and self.current_state == ProximityState.LOST
        )

        self.has_seen_target = True
        self.last_seen_at = now

        if returning_from_lost:
            self.rssi_window.clear()
            self._set_state(ProximityState.UNKNOWN, now)

        self.rssi_window.append(int(rssi))

        if len(self.rssi_window) < self.min_samples:
            return self.current_state

        average_rssi = self.average_rssi

        if average_rssi >= self.rssi_near:
            new_state = ProximityState.NEAR
        elif average_rssi <= self.rssi_away:
            new_state = ProximityState.AWAY
        else:
            new_state = ProximityState.UNCERTAIN

        self._set_state(new_state, now)

        # A stable NEAR state means the beacon has returned.
        # This only rearms future lock requests; it never unlocks Windows.
        if new_state == ProximityState.NEAR:
            self._reset_lock_latch()

        return self.current_state

    def check_timeouts(self, now: float | None = None) -> str:
        """
        Evaluate packet-loss timeout.

        Call this regularly, for example once per second, even when
        no BLE advertisements are received.
        """
        now = time.monotonic() if now is None else now

        if not self.has_seen_target or self.last_seen_at is None:
            return self.current_state

        seconds_since_seen = now - self.last_seen_at

        if (
            seconds_since_seen >= self.lost_after_seconds
            and self.current_state != ProximityState.LOST
        ):
            self.rssi_window.clear()
            self._set_state(ProximityState.LOST, now)

        return self.current_state

    def should_lock(self, now: float | None = None) -> bool:
        """
        Return True once when a lock request should be sent to policy.py.

        This method never locks Windows. It only emits a single logical
        lock request until the beacon returns and rearms the latch.
        """
        now = time.monotonic() if now is None else now

        if not self.has_seen_target:
            return False

        if self.lock_requested:
            return False

        seconds_in_state = now - self.state_entered_at

        if (
            self.current_state == ProximityState.AWAY
            and seconds_in_state >= self.lock_after_away_seconds
        ):
            self.lock_requested = True
            self.lock_reason = "away_timeout"
            return True

        if (
            self.current_state == ProximityState.LOST
            and seconds_in_state >= self.lock_after_lost_seconds
        ):
            self.lock_requested = True
            self.lock_reason = "lost_timeout"
            return True

        return False

    @property
    def average_rssi(self) -> float | None:
        """Return the current moving average, or None without samples."""
        if not self.rssi_window:
            return None

        return sum(self.rssi_window) / len(self.rssi_window)

    def snapshot(self, now: float | None = None) -> dict[str, Any]:
        """
        Return decision data for later logging, UI, or policy.py.

        No Windows action is performed here.
        """
        now = time.monotonic() if now is None else now

        last_seen_age_seconds: float | None = None
        if self.last_seen_at is not None:
            last_seen_age_seconds = now - self.last_seen_at

        return {
            "state": self.current_state,
            "average_rssi": self.average_rssi,
            "sample_count": len(self.rssi_window),
            "has_seen_target": self.has_seen_target,
            "last_seen_age_seconds": last_seen_age_seconds,
            "state_age_seconds": now - self.state_entered_at,
            "lock_requested": self.lock_requested,
            "lock_reason": self.lock_reason,
        }

    def _set_state(self, new_state: str, now: float) -> None:
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_entered_at = now

    def _reset_lock_latch(self) -> None:
        self.lock_requested = False
        self.lock_reason = None