# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CyberProff.no and contributors.
# This file is part of CyberKey.

"""Synthetic tests for the CyberKey policy engine."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from policy import PolicyAction, PolicyEngine  # noqa: E402


class PolicyEngineTests(unittest.TestCase):
    """Tests use synthetic timestamps and require no Windows APIs."""

    def make_engine(self, **overrides: object) -> PolicyEngine:
        config: dict[str, object] = {
            "enabled": True,
            "test_mode": True,
            "presentation_mode": False,
            "min_idle_seconds": 30,
            "cooldown_seconds": 60,
        }
        config.update(overrides)
        return PolicyEngine(config)

    def test_no_lock_request_returns_none(self) -> None:
        engine = self.make_engine()

        decision = engine.evaluate(
            lock_requested=False,
            lock_reason=None,
            idle_seconds=120,
            now=0.0,
        )

        self.assertEqual(decision.action, PolicyAction.NONE)
        self.assertEqual(decision.reason, "no_lock_request")
        self.assertFalse(engine.request_handled)

    def test_test_mode_returns_would_lock(self) -> None:
        engine = self.make_engine(test_mode=True)

        decision = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=30,
            now=10.0,
        )

        self.assertEqual(decision.action, PolicyAction.WOULD_LOCK)
        self.assertEqual(decision.reason, "test_mode")
        self.assertEqual(decision.lock_reason, "away_timeout")
        self.assertTrue(engine.request_handled)

    def test_non_test_mode_returns_lock_allowed(self) -> None:
        engine = self.make_engine(test_mode=False)

        decision = engine.evaluate(
            lock_requested=True,
            lock_reason="lost_timeout",
            idle_seconds=45,
            now=10.0,
        )

        self.assertEqual(decision.action, PolicyAction.LOCK_ALLOWED)
        self.assertEqual(decision.reason, "lock_allowed")
        self.assertEqual(decision.lock_reason, "lost_timeout")
        self.assertTrue(engine.request_handled)

    def test_same_request_is_handled_only_once(self) -> None:
        engine = self.make_engine()

        first = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=60,
            now=10.0,
        )
        second = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=60,
            now=11.0,
        )

        self.assertEqual(first.action, PolicyAction.WOULD_LOCK)
        self.assertEqual(second.action, PolicyAction.NONE)
        self.assertEqual(second.reason, "request_already_handled")

    def test_idle_threshold_blocks_until_requirement_is_met(self) -> None:
        engine = self.make_engine(min_idle_seconds=30)

        blocked = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=29,
            now=10.0,
        )

        self.assertEqual(blocked.action, PolicyAction.NONE)
        self.assertEqual(blocked.reason, "idle_threshold_not_met")
        self.assertFalse(engine.request_handled)

        allowed = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=30,
            now=11.0,
        )

        self.assertEqual(allowed.action, PolicyAction.WOULD_LOCK)
        self.assertEqual(allowed.reason, "test_mode")
        self.assertTrue(engine.request_handled)

    def test_disabled_policy_discards_request(self) -> None:
        engine = self.make_engine(enabled=False)

        decision = engine.evaluate(
            lock_requested=True,
            lock_reason="lost_timeout",
            idle_seconds=60,
            now=10.0,
        )

        self.assertEqual(decision.action, PolicyAction.NONE)
        self.assertEqual(decision.reason, "policy_disabled")
        self.assertTrue(engine.request_handled)

    def test_presentation_mode_discards_request(self) -> None:
        engine = self.make_engine(presentation_mode=True)

        decision = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=60,
            now=10.0,
        )

        self.assertEqual(decision.action, PolicyAction.NONE)
        self.assertEqual(decision.reason, "presentation_mode")
        self.assertTrue(engine.request_handled)

    def test_cooldown_blocks_new_request_until_expired(self) -> None:
        engine = self.make_engine(cooldown_seconds=60)

        first = engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=60,
            now=10.0,
        )
        engine.evaluate(
            lock_requested=False,
            lock_reason=None,
            idle_seconds=60,
            now=11.0,
        )

        blocked = engine.evaluate(
            lock_requested=True,
            lock_reason="lost_timeout",
            idle_seconds=60,
            now=20.0,
        )
        allowed = engine.evaluate(
            lock_requested=True,
            lock_reason="lost_timeout",
            idle_seconds=60,
            now=70.0,
        )

        self.assertEqual(first.action, PolicyAction.WOULD_LOCK)

        self.assertEqual(blocked.action, PolicyAction.NONE)
        self.assertEqual(blocked.reason, "cooldown_active")
        self.assertAlmostEqual(
            blocked.cooldown_remaining_seconds,
            50.0,
        )

        self.assertEqual(allowed.action, PolicyAction.WOULD_LOCK)
        self.assertEqual(allowed.reason, "test_mode")

    def test_negative_idle_seconds_is_rejected(self) -> None:
        engine = self.make_engine()

        with self.assertRaises(ValueError):
            engine.evaluate(
                lock_requested=True,
                lock_reason="away_timeout",
                idle_seconds=-1,
                now=10.0,
            )

    def test_snapshot_reports_current_policy_state(self) -> None:
        engine = self.make_engine(
            enabled=True,
            test_mode=True,
            presentation_mode=False,
            min_idle_seconds=30,
            cooldown_seconds=60,
        )

        engine.evaluate(
            lock_requested=True,
            lock_reason="away_timeout",
            idle_seconds=60,
            now=10.0,
        )

        snapshot = engine.snapshot(now=20.0)

        self.assertTrue(snapshot["enabled"])
        self.assertTrue(snapshot["test_mode"])
        self.assertFalse(snapshot["presentation_mode"])
        self.assertEqual(snapshot["min_idle_seconds"], 30.0)
        self.assertEqual(snapshot["cooldown_seconds"], 60.0)
        self.assertTrue(snapshot["request_handled"])
        self.assertEqual(snapshot["last_action_at"], 10.0)
        self.assertAlmostEqual(
            snapshot["cooldown_remaining_seconds"],
            50.0,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)