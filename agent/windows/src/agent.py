"""
CyberKey Dry-Run Agent

Purpose:

- Accept synthetic RSSI samples and deterministic timeout ticks.
- Drive the proximity and policy engines in the intended order.
- Return policy decisions for safe dry-run observation.

Security boundary:

- This module accepts caller-supplied synthetic input only.
- It performs no live device discovery, OS action, unlock,
  authentication, or access-control behavior.
- DryRunAgent always forces policy test mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from policy import PolicyDecision, PolicyEngine
from proximity import ProximityEngine


@dataclass(frozen=True)
class AgentResult:
    """Result from one synthetic agent step."""

    now: float
    event_type: str
    rssi: int | None
    proximity_state: str
    lock_requested: bool
    lock_reason: str | None
    policy_decision: PolicyDecision

    @property
    def action(self) -> str:
        """Return the policy action for concise dry-run output."""

        return self.policy_decision.action


class DryRunAgent:
    """
    Safe synthetic orchestration layer.

    RSSI samples and timeout ticks are supplied explicitly by the caller.
    All timestamps are deterministic and must be non-decreasing.
    """

    def __init__(
        self,
        *,
        proximity_config: dict[str, Any] | None = None,
        policy_config: dict[str, Any] | None = None,
    ) -> None:
        policy_config = dict(policy_config or {})

        if (
            "test_mode" in policy_config
            and not bool(policy_config["test_mode"])
        ):
            raise ValueError(
                "DryRunAgent requires policy test_mode=True."
            )

        policy_config["test_mode"] = True

        self.proximity = ProximityEngine(config=proximity_config)
        self.policy = PolicyEngine(config=policy_config)

        self._last_now: float | None = None

    def process_rssi(
        self,
        *,
        rssi: int,
        idle_seconds: float,
        now: float,
    ) -> AgentResult:
        """Process one synthetic RSSI sample."""

        now, idle_seconds = self._prepare_inputs(
            now=now,
            idle_seconds=idle_seconds,
        )
        rssi = int(rssi)

        self.proximity.update(rssi=rssi, now=now)

        return self._evaluate(
            now=now,
            idle_seconds=idle_seconds,
            event_type="rssi",
            rssi=rssi,
        )

    def process_timeout(
        self,
        *,
        idle_seconds: float,
        now: float,
    ) -> AgentResult:
        """Process one synthetic timeout tick without an RSSI sample."""

        now, idle_seconds = self._prepare_inputs(
            now=now,
            idle_seconds=idle_seconds,
        )

        self.proximity.check_timeouts(now=now)

        return self._evaluate(
            now=now,
            idle_seconds=idle_seconds,
            event_type="timeout",
            rssi=None,
        )

    def _prepare_inputs(
        self,
        *,
        now: float,
        idle_seconds: float,
    ) -> tuple[float, float]:
        try:
            normalized_now = float(now)
            normalized_idle_seconds = float(idle_seconds)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "now and idle_seconds must be numeric values."
            ) from exc

        if normalized_now < 0:
            raise ValueError("now cannot be negative.")

        if self._last_now is not None and normalized_now < self._last_now:
            raise ValueError("now must be non-decreasing.")

        if normalized_idle_seconds < 0:
            raise ValueError("idle_seconds cannot be negative.")

        self._last_now = normalized_now
        return normalized_now, normalized_idle_seconds

    def _evaluate(
        self,
        *,
        now: float,
        idle_seconds: float,
        event_type: str,
        rssi: int | None,
    ) -> AgentResult:
        """
        Evaluate the current proximity state through policy.

        The proximity latch is retained after its one-shot request so a
        denied request can be re-evaluated when idle time or cooldown
        conditions later permit it.
        """

        self.proximity.should_lock(now=now)

        decision = self.policy.evaluate(
            lock_requested=self.proximity.lock_requested,
            lock_reason=self.proximity.lock_reason,
            idle_seconds=idle_seconds,
            now=now,
        )

        return AgentResult(
            now=now,
            event_type=event_type,
            rssi=rssi,
            proximity_state=self.proximity.current_state,
            lock_requested=self.proximity.lock_requested,
            lock_reason=self.proximity.lock_reason,
            policy_decision=decision,
        )
