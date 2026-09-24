import unittest
from unittest.mock import patch

from dice_progression import PlayerDicePool
from player_state import Player
from progression import PlayerProgress
from session_resolution import resolve_session_plan
from session_risk import (
    base_bust_threshold,
    first_bust_index,
    is_risk_tentable,
)
from session_selector import choose_sessions_weighted
from simulate_player import play_player_turn


RISK_FRIENDLY_WEIGHTS = {
    "w_energy": 0.0,
    "w_sessions": 10.0,
    "w_fatigue": 0.0,
    "w_rpe": 1.0,
}


class TestTentableCatalogProgression(unittest.TestCase):
    def test_unlocked_predecessor_without_completion_does_not_open_successor(self):
        progress = PlayerProgress()
        progress.completions["Spec5"] = 2

        self.assertIn("Spec6", progress.available_sessions())
        self.assertIn("Spec6", progress.tentable_sessions())
        self.assertNotIn("Spec7", progress.tentable_sessions())

    def test_one_success_opens_only_immediate_successor(self):
        progress = PlayerProgress()
        progress.completions["Spec5"] = 2
        progress.completions["Spec6"] = 1

        self.assertNotIn("Spec7", progress.available_sessions())
        self.assertIn("Spec7", progress.tentable_sessions())
        self.assertNotIn("Spec8", progress.tentable_sessions())

    def test_normal_threshold_unlocks_successor_but_not_following_level(self):
        progress = PlayerProgress()
        progress.completions["Spec5"] = 2
        progress.completions["Spec6"] = 2

        self.assertIn("Spec7", progress.available_sessions())
        self.assertIn("Spec7", progress.tentable_sessions())
        self.assertNotIn("Spec8", progress.tentable_sessions())

    def test_multibranch_entry_uses_explicit_predecessor_graph(self):
        progress = PlayerProgress()
        progress.completions["EF2"] = 2

        self.assertIn("Seuil3", progress.available_sessions())
        self.assertNotIn("Spec4", progress.tentable_sessions())

        progress.completions["Seuil3"] = 1
        self.assertNotIn("Spec4", progress.available_sessions())
        self.assertIn("Spec4", progress.tentable_sessions())


class TestRiskBoundaries(unittest.TestCase):
    def test_safe_session_consumes_no_roll(self):
        calls = []
        result = first_bust_index(
            ["EF4", "Seuil4"], 4, [6, 6, 8, 10],
            lambda size: calls.append(size) or 1,
        )
        self.assertIsNone(result)
        self.assertEqual(calls, [])

    def test_plus_one_boundary(self):
        self.assertEqual(first_bust_index(["Seuil5"], 4, [6], lambda _: 1), 0)
        self.assertIsNone(first_bust_index(["Seuil5"], 4, [6], lambda _: 2))

    def test_plus_two_boundary(self):
        self.assertEqual(first_bust_index(["VMA6"], 4, [8], lambda _: 2), 0)
        self.assertIsNone(first_bust_index(["VMA6"], 4, [8], lambda _: 3))

    def test_largest_persistent_die_is_used(self):
        sizes_seen = []
        first_bust_index(
            ["Seuil5"], 4, [6, 6, 8, 10],
            lambda size: sizes_seen.append(size) or 2,
        )
        self.assertEqual(sizes_seen, [10])

    def test_raw_face_not_bonus_value_is_used(self):
        with patch("session_risk.Die.roll", return_value=(1, 99)):
            self.assertEqual(first_bust_index(["Seuil5"], 4, [10]), 0)

    def test_certain_bust_is_not_tentable(self):
        self.assertFalse(is_risk_tentable("Spec9", rpe_max=3, best_die_size=6))
        self.assertTrue(is_risk_tentable("Spec9", rpe_max=4, best_die_size=6))

    def test_threshold_is_isolated(self):
        self.assertEqual(base_bust_threshold(6, 4), 2)
        self.assertEqual(base_bust_threshold(4, 4), 0)


class TestRiskOrder(unittest.TestCase):
    def test_multiple_successes_follow_program_order(self):
        rolls = iter([2, 3, 2])
        self.assertIsNone(first_bust_index(
            ["Seuil5", "VMA6", "Force5"], 4, [10], lambda _: next(rolls),
        ))

    def test_first_bust_stops_later_rolls(self):
        rolls = iter([1, 9, 9])
        calls = []
        index = first_bust_index(
            ["Seuil5", "VMA6", "Force5"], 4, [10],
            lambda _: calls.append(True) or next(rolls),
        )
        self.assertEqual(index, 0)
        self.assertEqual(len(calls), 1)

    def test_intermediate_bust_preserves_exact_plan_index(self):
        rolls = iter([5, 2, 9])
        calls = []
        index = first_bust_index(
            ["EF1", "Seuil5", "EF2", "VMA6", "Force5"], 4, [10],
            lambda _: calls.append(True) or next(rolls),
        )
        self.assertEqual(index, 3)
        self.assertEqual(len(calls), 2)


class TestSelectorAndTurnIntegration(unittest.TestCase):
    def test_selector_can_choose_risky_quality(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "Seuil5"], 10, 4, 10, 1,
            weights=RISK_FRIENDLY_WEIGHTS, best_die_size=6,
        )
        self.assertIn("Seuil5", chosen)

    def test_selector_rejects_certain_bust(self):
        chosen, _ = choose_sessions_weighted(
            ["EF1", "Spec9"], 20, 3, 10, 1,
            weights=RISK_FRIENDLY_WEIGHTS, best_die_size=6,
        )
        self.assertNotIn("Spec9", chosen)

    def test_produced_bust_index_reaches_existing_resolver(self):
        player = Player(dice_pool=PlayerDicePool(sizes=[6, 6, 8, 10]))
        roll = {
            "energy_budget": 10, "rpe_max": 4, "quality_sessions_from_roll": 1,
            "tn": 20, "pool_size": 4, "final_faces": [1, 1, 1],
            "final_values": [1, 1, 1], "pattern": "test", "action_chosen": "keep",
        }
        plan = ["EF1", "Seuil5"]
        trace = [{"session": name, "note": ""} for name in plan]
        player.progress.available_sessions = lambda: ["EF1", "Seuil5"]
        player.progress.tentable_sessions = lambda: ["EF1", "Seuil5"]
        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted", return_value=(plan, trace)
        ):
            turn, _ = play_player_turn(1, player, risk_roll_face=lambda _: 1)

        self.assertEqual(turn["energy_lost"], 5)
        self.assertEqual(turn["sessions_completed"], "EF1")
        self.assertEqual(player.progress.quality_total, 0)


if __name__ == "__main__":
    unittest.main()
