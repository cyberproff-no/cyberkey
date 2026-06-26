# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CyberProff.no and contributors.
# This file is part of CyberKey.

"""
CyberKey Policy Engine

Purpose:
- Receive lock-request decisions from the proximity engine.
- Apply operational safety rules before any lock action is allowed.
- Keep policy decisions separate from Windows-specific locking.

Security rule:
This module must never unlock Windows, authenticate users,
or call the Windows lock API directly.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


class PolicyAction:
    NONE = "NONE"
    WOULD_LOCK = "WOULD_LOCK"
    LOCK_ALLOWED = "LOCK_ALLOWED"


@dataclass(frozen=True)
class PolicyDecision:
    """Result returned by the policy engine."""

    action: str
    reason: str
    lock_reason: str | None
    cooldown_remaining_seconds: float = 0.0


class PolicyEngine:
    """
    Pure policy engine.

    The caller provides:
    - lock_requested from the proximity engine
    - lock_reason from the proximity engine
    - idle_seconds from a future idle-time provider
    - now for deterministic tests

    This class does not call locker.py yet.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}

        self.enabled = bool(config.get("enabled", True))
        self.test_mode = bool(config.get("test_mode", True))
        self.presentation_mode = bool(
            config.get("presentation_mode", False)
        )

        self.min_idle_seconds = float(
            config.get("min_idle_seconds", 30)
        )
        self.cooldown_seconds = float(
            config.get("cooldown_seconds", 30)
        )

        self._validate_config()

        self.last_action_at: float | None = None
        self._request_handled = False

    def _validate_config(self) -> None:
        if self.min_idle_seconds < 0:
            raise ValueError("min_idle_seconds cannot be negative.")

        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative.")

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable policy actions."""

        self.enabled = bool(enabled)

    def set_presentation_mode(self, enabled: bool) -> None:
        """Enable or disable presentation mode."""

        self.presentation_mode = bool(enabled)

    def evaluate(
        self,
        *,
        lock_requested: bool,
        lock_reason: str | None,
        idle_seconds: float,
        now: float | None = None,
    ) -> PolicyDecision:
        """
        Evaluate whether a proximity lock request may become an action.

        In test mode, a successful evaluation returns WOULD_LOCK.
        Outside test mode, it returns LOCK_ALLOWED.

        No Windows action is performed here.
        """
        now = time.monotonic() if now is None else now

        if idle_seconds < 0:
            raise ValueError("idle_seconds cannot be negative.")

        if not lock_requested:
            self._request_handled = False
            return self._decision(
                action=PolicyAction.NONE,
                reason="no_lock_request",
                lock_reason=None,
                now=now,
            )

        if self._request_handled:
            return self._decision(
                action=PolicyAction.NONE,
                reason="request_already_handled",
                lock_reason=lock_reason,
                now=now,
            )

        if not self.enabled:
            self._request_handled = True
            return self._decision(
                action=PolicyAction.NONE,
                reason="policy_disabled",
                lock_reason=lock_reason,
                now=now,
            )

        if self.presentation_mode:
            self._request_handled = True
            return self._decision(
                action=PolicyAction.NONE,
                reason="presentation_mode",
                lock_reason=lock_reason,
                now=now,
            )

        if idle_seconds < self.min_idle_seconds:
            return self._decision(
                action=PolicyAction.NONE,
                reason="idle_threshold_not_met",
                lock_reason=lock_reason,
                now=now,
            )

        cooldown_remaining = self._cooldown_remaining(now)
        if cooldown_remaining > 0:
            return PolicyDecision(
                action=PolicyAction.NONE,
                reason="cooldown_active",
                lock_reason=lock_reason,
                cooldown_remaining_seconds=cooldown_remaining,
            )

        action = (
            PolicyAction.WOULD_LOCK
            if self.test_mode
            else PolicyAction.LOCK_ALLOWED
        )

        self.last_action_at = now
        self._request_handled = True

        return self._decision(
            action=action,
            reason="test_mode" if self.test_mode else "lock_allowed",
            lock_reason=lock_reason,
            now=now,
        )

    @property
    def request_handled(self) -> bool:
        """Return whether the current proximity request was handled."""

        return self._request_handled

    def snapshot(self, now: float | None = None) -> dict[str, Any]:
        """Return policy state for logging, UI, or later integration."""

        now = time.monotonic() if now is None else now

        return {
            "enabled": self.enabled,
            "test_mode": self.test_mode,
            "presentation_mode": self.presentation_mode,
            "min_idle_seconds": self.min_idle_seconds,
            "cooldown_seconds": self.cooldown_seconds,
            "cooldown_remaining_seconds": self._cooldown_remaining(now),
            "request_handled": self._request_handled,
            "last_action_at": self.last_action_at,
        }

    def _decision(
        self,
        *,
        action: str,
        reason: str,
        lock_reason: str | None,
        now: float,
    ) -> PolicyDecision:
        return PolicyDecision(
            action=action,
            reason=reason,
            lock_reason=lock_reason,
            cooldown_remaining_seconds=self._cooldown_remaining(now),
        )

    def _cooldown_remaining(self, now: float) -> float:
        if self.last_action_at is None:
            return 0.0

        elapsed = now - self.last_action_at
        return max(0.0, self.cooldown_seconds - elapsed)