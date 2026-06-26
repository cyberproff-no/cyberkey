# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 CyberProff.no and contributors.
# This file is part of CyberKey.

"""Synthetic tests for the CyberKey proximity state machine."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from proximity import ProximityEngine, ProximityState  # noqa: E402


class ProximityEngineTests(unittest.TestCase):
    """Tests use synthetic timestamps; no BLE hardware is required."""

    def make_engine(self, **overrides: object) -> ProximityEngine:
        config: dict[str, object] = {
            "rssi_near": -65,
            "rssi_away": -80,
            "window_size": 5,
            "min_samples": 3,
            "lost_after_seconds": 5,
            "lock_after_away_seconds": 4,
            "lock_after_lost_seconds": 3,
        }
        config.update(overrides)
        return ProximityEngine(config)

    @staticmethod
    def feed(
        engine: ProximityEngine,
        samples: list[int],
        start: float = 0.0,
    ) -> str:
        state = engine.current_state

        for offset, rssi in enumerate(samples):
            state = engine.update(rssi, now=start + offset)

        return state

    def test_beacon_never_observed_never_locks(self) -> None:
        engine = self.make_engine()

        self.assertEqual(engine.current_state, ProximityState.UNKNOWN)
        self.assertEqual(
            engine.check_timeouts(now=10_000.0),
            ProximityState.UNKNOWN,
        )
        self.assertFalse(engine.should_lock(now=10_000.0))

    def test_stable_strong_rssi_becomes_near(self) -> None:
        engine = self.make_engine()

        state = self.feed(engine, [-55, -56, -54])

        self.assertEqual(state, ProximityState.NEAR)
        self.assertEqual(engine.current_state, ProximityState.NEAR)
        self.assertAlmostEqual(engine.average_rssi or 0.0, -55.0)

    def test_noise_in_gray_zone_stays_uncertain(self) -> None:
        engine = self.make_engine()
        samples = [-66, -64, -67, -65, -64, -66]
        observed_states = []

        for timestamp, rssi in enumerate(samples):
            observed_states.append(engine.update(rssi, now=float(timestamp)))

        self.assertEqual(
            observed_states[2:],
            [
                ProximityState.UNCERTAIN,
                ProximityState.UNCERTAIN,
                ProximityState.UNCERTAIN,
                ProximityState.UNCERTAIN,
            ],
        )
        self.assertEqual(engine.current_state, ProximityState.UNCERTAIN)

    def test_stable_weak_rssi_becomes_away(self) -> None:
        engine = self.make_engine()

        state = self.feed(engine, [-84, -83, -85])

        self.assertEqual(state, ProximityState.AWAY)
        self.assertEqual(engine.current_state, ProximityState.AWAY)

    def test_missing_packets_become_lost_after_separate_timeout(self) -> None:
        engine = self.make_engine(lost_after_seconds=5)

        self.feed(engine, [-55, -56, -54])
        self.assertEqual(engine.current_state, ProximityState.NEAR)

        self.assertEqual(
            engine.check_timeouts(now=6.9),
            ProximityState.NEAR,
        )
        self.assertEqual(
            engine.check_timeouts(now=7.0),
            ProximityState.LOST,
        )

    def test_away_timeout_emits_one_lock_request(self) -> None:
        engine = self.make_engine(lock_after_away_seconds=4)

        self.feed(engine, [-84, -83, -85])
        self.assertEqual(engine.current_state, ProximityState.AWAY)

        self.assertFalse(engine.should_lock(now=5.9))
        self.assertTrue(engine.should_lock(now=6.0))
        self.assertEqual(engine.lock_reason, "away_timeout")
        self.assertFalse(engine.should_lock(now=7.0))

    def test_lost_timeout_emits_one_lock_request(self) -> None:
        engine = self.make_engine(
            lost_after_seconds=5,
            lock_after_lost_seconds=3,
        )

        self.feed(engine, [-55, -56, -54])
        engine.check_timeouts(now=7.0)
        self.assertEqual(engine.current_state, ProximityState.LOST)

        self.assertFalse(engine.should_lock(now=9.9))
        self.assertTrue(engine.should_lock(now=10.0))
        self.assertEqual(engine.lock_reason, "lost_timeout")
        self.assertFalse(engine.should_lock(now=11.0))

    def test_beacon_return_after_lost_rearms_only_after_near(self) -> None:
        engine = self.make_engine(
            lost_after_seconds=5,
            lock_after_lost_seconds=3,
        )

        self.feed(engine, [-55, -56, -54])
        engine.check_timeouts(now=7.0)

        self.assertTrue(engine.should_lock(now=10.0))
        self.assertTrue(engine.lock_requested)

        self.assertEqual(
            engine.update(-55, now=11.0),
            ProximityState.UNKNOWN,
        )
        self.assertTrue(engine.lock_requested)
        self.assertEqual(engine.lock_reason, "lost_timeout")

        self.assertEqual(
            engine.update(-56, now=12.0),
            ProximityState.UNKNOWN,
        )
        self.assertEqual(
            engine.update(-54, now=13.0),
            ProximityState.NEAR,
        )
        self.assertFalse(engine.lock_requested)
        self.assertIsNone(engine.lock_reason)

    def test_latch_rearms_only_after_stable_near_return(self) -> None:
        engine = self.make_engine(lock_after_away_seconds=4)

        self.feed(engine, [-84, -83, -85])

        self.assertTrue(engine.should_lock(now=6.0))
        self.assertTrue(engine.lock_requested)

        engine.update(-50, now=7.0)
        engine.update(-50, now=8.0)
        self.assertTrue(engine.lock_requested)

        self.assertEqual(
            engine.update(-50, now=9.0),
            ProximityState.NEAR,
        )
        self.assertFalse(engine.lock_requested)
        self.assertIsNone(engine.lock_reason)


if __name__ == "__main__":
    unittest.main(verbosity=2)