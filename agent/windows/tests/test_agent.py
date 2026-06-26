# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CyberProff.no and contributors.
# This file is part of CyberKey.

"""
End-to-end tests for the CyberKey synthetic dry-run agent.

These tests verify the safe data flow:

synthetic RSSI or timeout event
-> ProximityEngine
-> PolicyEngine
-> WOULD_LOCK or NONE

No live BLE scanning, Windows locking, or locker.py integration is used.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

AGENT_MODULE_PATH = SRC_DIR / "agent.py"
_spec = importlib.util.spec_from_file_location(
    "cyberkey_dry_run_agent",
    AGENT_MODULE_PATH,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load module from {AGENT_MODULE_PATH}")
_agent_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _agent_module
_spec.loader.exec_module(_agent_module)
DryRunAgent = _agent_module.DryRunAgent

from policy import PolicyAction
from proximity import ProximityState

DEFAULT_PROXIMITY_CONFIG = {
    "rssi_near": -65,
    "rssi_away": -80,
    "window_size": 1,
    "min_samples": 1,
    "lost_after_seconds": 60,
    "lock_after_away_seconds": 5,
    "lock_after_lost_seconds": 4,
}

DEFAULT_POLICY_CONFIG = {
    "enabled": True,
    "test_mode": True,
    "presentation_mode": False,
    "min_idle_seconds": 0,
    "cooldown_seconds": 0,
}


class TestDryRunAgent(unittest.TestCase):
    """Synthetic end-to-end coverage for DryRunAgent."""

    def make_agent(
        self,
        *,
        proximity_overrides: dict[str, int | float] | None = None,
        policy_overrides: dict[str, bool | int | float] | None = None,
    ) -> DryRunAgent:
        proximity_config = dict(DEFAULT_PROXIMITY_CONFIG)
        policy_config = dict(DEFAULT_POLICY_CONFIG)

        if proximity_overrides:
            proximity_config.update(proximity_overrides)

        if policy_overrides:
            policy_config.update(policy_overrides)

        return DryRunAgent(
            proximity_config=proximity_config,
            policy_config=policy_config,
        )

    def test_strong_rssi_becomes_near_without_action(self) -> None:
        """Strong RSSI enters NEAR and produces no policy action."""

        agent = self.make_agent()

        result = agent.process_rssi(
            rssi=-50,
            idle_seconds=300,
            now=0,
        )

        self.assertEqual(result.proximity_state, ProximityState.NEAR)
        self.assertFalse(result.lock_requested)
        self.assertEqual(result.action, PolicyAction.NONE)
        self.assertEqual(
            result.policy_decision.reason,
            "no_lock_request",
        )

    def test_weak_rssi_for_away_timeout_returns_would_lock(self) -> None:
        """Weak RSSI held long enough enters AWAY and returns WOULD_LOCK."""

        agent = self.make_agent(
            proximity_overrides={
                "lock_after_away_seconds": 5,
            }
        )

        initial = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=0,
        )
        result = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=5,
        )

        self.assertEqual(initial.proximity_state, ProximityState.AWAY)
        self.assertEqual(initial.action, PolicyAction.NONE)

        self.assertEqual(result.proximity_state, ProximityState.AWAY)
        self.assertTrue(result.lock_requested)
        self.assertEqual(result.lock_reason, "away_timeout")
        self.assertEqual(result.action, PolicyAction.WOULD_LOCK)
        self.assertEqual(result.policy_decision.reason, "test_mode")

    def test_missing_packets_for_lost_timeout_returns_would_lock(self) -> None:
        """Missing packets enter LOST and later return WOULD_LOCK."""

        agent = self.make_agent(
            proximity_overrides={
                "lost_after_seconds": 3,
                "lock_after_lost_seconds": 4,
            }
        )

        agent.process_rssi(
            rssi=-50,
            idle_seconds=60,
            now=0,
        )

        lost = agent.process_timeout(
            idle_seconds=60,
            now=3,
        )
        result = agent.process_timeout(
            idle_seconds=60,
            now=7,
        )

        self.assertEqual(lost.proximity_state, ProximityState.LOST)
        self.assertEqual(lost.action, PolicyAction.NONE)

        self.assertEqual(result.proximity_state, ProximityState.LOST)
        self.assertTrue(result.lock_requested)
        self.assertEqual(result.lock_reason, "lost_timeout")
        self.assertEqual(result.action, PolicyAction.WOULD_LOCK)

    def test_idle_threshold_blocks_until_idle_requirement_is_met(self) -> None:
        """A valid proximity request waits until enough idle time exists."""

        agent = self.make_agent(
            policy_overrides={
                "min_idle_seconds": 30,
            }
        )

        agent.process_rssi(
            rssi=-90,
            idle_seconds=0,
            now=0,
        )
        blocked = agent.process_rssi(
            rssi=-90,
            idle_seconds=29,
            now=5,
        )
        allowed = agent.process_timeout(
            idle_seconds=30,
            now=6,
        )

        self.assertTrue(blocked.lock_requested)
        self.assertEqual(blocked.action, PolicyAction.NONE)
        self.assertEqual(
            blocked.policy_decision.reason,
            "idle_threshold_not_met",
        )

        self.assertTrue(allowed.lock_requested)
        self.assertEqual(allowed.action, PolicyAction.WOULD_LOCK)

    def test_cooldown_blocks_later_request_until_expiry(self) -> None:
        """Cooldown blocks a later departure cycle before allowing it."""

        agent = self.make_agent(
            proximity_overrides={
                "lock_after_away_seconds": 2,
            },
            policy_overrides={
                "cooldown_seconds": 10,
            },
        )

        agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=0,
        )
        first_action = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=2,
        )

        agent.process_rssi(
            rssi=-50,
            idle_seconds=60,
            now=3,
        )
        agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=4,
        )
        blocked = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=6,
        )
        allowed = agent.process_timeout(
            idle_seconds=60,
            now=12,
        )

        self.assertEqual(first_action.action, PolicyAction.WOULD_LOCK)

        self.assertTrue(blocked.lock_requested)
        self.assertEqual(blocked.action, PolicyAction.NONE)
        self.assertEqual(
            blocked.policy_decision.reason,
            "cooldown_active",
        )
        self.assertGreater(
            blocked.policy_decision.cooldown_remaining_seconds,
            0,
        )

        self.assertEqual(allowed.action, PolicyAction.WOULD_LOCK)

    def test_proximity_and_policy_latches_prevent_repeat_would_lock(self) -> None:
        """One departure cycle emits WOULD_LOCK only once."""

        agent = self.make_agent(
            proximity_overrides={
                "lock_after_away_seconds": 2,
            }
        )

        agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=0,
        )
        first_action = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=2,
        )
        repeated = agent.process_timeout(
            idle_seconds=60,
            now=3,
        )

        self.assertEqual(first_action.action, PolicyAction.WOULD_LOCK)
        self.assertTrue(agent.proximity.lock_requested)
        self.assertTrue(agent.policy.request_handled)

        self.assertEqual(repeated.action, PolicyAction.NONE)
        self.assertEqual(
            repeated.policy_decision.reason,
            "request_already_handled",
        )

    def test_stable_near_return_rearms_a_future_departure_cycle(self) -> None:
        """Stable NEAR clears latches and permits a later WOULD_LOCK."""

        agent = self.make_agent(
            proximity_overrides={
                "lock_after_away_seconds": 2,
            }
        )

        agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=0,
        )
        first_action = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=2,
        )

        returned = agent.process_rssi(
            rssi=-50,
            idle_seconds=60,
            now=3,
        )

        self.assertEqual(first_action.action, PolicyAction.WOULD_LOCK)

        self.assertEqual(returned.proximity_state, ProximityState.NEAR)
        self.assertFalse(returned.lock_requested)
        self.assertFalse(agent.policy.request_handled)
        self.assertEqual(returned.action, PolicyAction.NONE)

        agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=4,
        )
        second_action = agent.process_rssi(
            rssi=-90,
            idle_seconds=60,
            now=6,
        )

        self.assertEqual(second_action.proximity_state, ProximityState.AWAY)
        self.assertEqual(second_action.action, PolicyAction.WOULD_LOCK)


if __name__ == "__main__":
    unittest.main()
