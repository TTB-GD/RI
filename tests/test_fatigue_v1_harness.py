import random
import unittest

from fatigue_v1_harness import (BUST, NORMAL, RISK_SUCCESS, UNTESTED, FatigueState,
                                _active_indices, resolve_sessions, simulate)
from player_state import Player


class TestFatigueV1Resolution(unittest.TestCase):
    def test_first_bust_cancels_only_its_risk_session_and_stops_later_risk_rolls(self):
        random.seed(1)  # first d6 roll is 2
        rows = resolve_sessions(["EF1", "Seuil3", "VMA3", "EF1"], rpe_max=1, best_die=6)
        self.assertEqual([row["status"] for row in rows], [NORMAL, BUST, UNTESTED, NORMAL])
        self.assertEqual(rows[1]["bust_roll"], 2)
        self.assertIsNone(rows[2]["bust_roll"])

    def test_disabled_bust_realizes_risk_sessions_but_consumes_matched_draw(self):
        rows = resolve_sessions(["Seuil3"], rpe_max=1, best_die=6, bust_enabled=False)
        self.assertEqual(rows[0]["status"], RISK_SUCCESS)
        self.assertIsNotNone(rows[0]["bust_roll"])


class TestFatigueV1Boundaries(unittest.TestCase):
    def test_removed_die_recovers_at_equal_boundary_not_plus_one(self):
        player = Player()
        state = FatigueState(fatigue=7, suspended_index=3)
        active, recovered = _active_indices(player, state)
        self.assertFalse(recovered)
        self.assertEqual(active, [0, 1, 2])
        state.fatigue = 6
        active, recovered = _active_indices(player, state)
        self.assertTrue(recovered)
        self.assertEqual(active, [0, 1, 2, 3])

    def test_turn_rows_use_effective_not_planned_work_for_ctl(self):
        turns, sessions = simulate(seed=3, turns=4, policy="risk")
        for row in turns:
            realized_cost = sum(s["rpe"] for s in sessions if s["turn"] == row["turn"] and s["realized"])
            self.assertEqual(row["spend_effective"], realized_cost)
            self.assertGreaterEqual(row["spend_planned"], row["spend_effective"])


if __name__ == "__main__":
    unittest.main()
