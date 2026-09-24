import unittest
from unittest.mock import patch

from decision_engine import energy_and_fatigue
from player_state import Player
from session_resolution import resolve_session_plan
from session_selector import choose_sessions_weighted
from sessions_catalog import QUALITY_CATEGORIES, SESSION_CATALOG
from simulate_player import play_player_turn


NO_FATIGUE_WEIGHTS = {
    "w_energy": 3.0,
    "w_sessions": 10.0,
    "w_fatigue": 0.0,
    "w_rpe": 0.25,
}


class TestD99AndRepetition(unittest.TestCase):
    def choose(self, names, d99, energy=40, rpe=9):
        return choose_sessions_weighted(
            names, energy, rpe, 20, d99, weights=NO_FATIGUE_WEIGHTS,
        )[0]

    def test_d99_zero_blocks_quality_but_not_ef(self):
        chosen = self.choose(["EF1", "Seuil3"], 0)
        self.assertIn("EF1", chosen)
        self.assertNotIn("Seuil3", chosen)

    def test_d99_caps_quality_and_includes_sl(self):
        chosen = self.choose(["EF1", "Seuil3", "VMA3", "SL5"], 1)
        quality = [n for n in chosen if SESSION_CATALOG[n][0] in QUALITY_CATEGORIES]
        self.assertEqual(quality, ["SL5"])

    def test_quality_entries_unique_but_different_entries_allowed(self):
        chosen = self.choose(["EF1", "Seuil3", "VMA3"], 2)
        quality = [n for n in chosen if SESSION_CATALOG[n][0] in QUALITY_CATEGORIES]
        self.assertEqual(len(quality), len(set(quality)))
        self.assertEqual(set(quality), {"Seuil3", "VMA3"})

    def test_ef_repeats_and_global_limit_is_seven(self):
        chosen = self.choose(["EF1"], 0)
        self.assertEqual(chosen, ["EF1"] * 7)


class TestPostBustResolution(unittest.TestCase):
    available = ["EF1", "EF2", "EF3", "EF4", "EF5", "Seuil3", "Seuil5", "VMA5", "Force5", "Spec9", "SL9"]

    def test_busted_session_counts_and_loses_energy(self):
        result = resolve_session_plan(["EF4", "Seuil5"], self.available, 4, 1)
        self.assertEqual(result.counted_sessions, ("EF4", "Seuil5"))
        self.assertEqual(result.completed_sessions, ("EF4",))
        self.assertEqual(result.energy_lost, 5)

    def test_later_risks_are_cancelled_and_replaced_with_ef(self):
        result = resolve_session_plan(
            ["EF1", "Seuil5", "EF1", "VMA5"], self.available, 4, 1,
        )
        self.assertEqual(result.cancelled_sessions, ("VMA5",))
        self.assertEqual(result.replacement_sessions, ("EF4", "EF1"))
        self.assertNotIn("VMA5", result.completed_sessions)

    def test_normal_later_sessions_remain(self):
        result = resolve_session_plan(
            ["EF1", "Seuil5", "EF2", "Seuil3"], self.available, 4, 1,
        )
        self.assertEqual(result.cancelled_sessions, ())
        self.assertIn("EF2", result.completed_sessions)
        self.assertIn("Seuil3", result.completed_sessions)

    def test_redistribution_is_limited_by_remaining_session_slots(self):
        result = resolve_session_plan(
            ["EF1", "EF1", "EF1", "Seuil5", "Spec9", "SL9"],
            self.available, 4, 3,
        )
        self.assertEqual(len(result.counted_sessions), 7)
        self.assertEqual(len(result.replacement_sessions), 3)
        self.assertEqual(result.stop_reason, "seven_session_limit")

    def test_turn_fatigue_and_progression_use_only_effective_load(self):
        player = Player()
        roll = {
            "energy_budget": 12, "rpe_max": 4, "quality_sessions_from_roll": 2,
            "tn": 20, "pool_size": 4, "final_values": [1, 1, 1],
            "pattern": "test", "action_chosen": "keep",
        }
        plan = ["EF1", "Seuil5", "EF1", "VMA5"]
        trace = [
            {"session": name, "marginal_utility": 1, "alternatives_considered": 1, "note": ""}
            for name in plan
        ]
        player.progress.available_sessions = lambda: self.available
        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted", return_value=(plan, trace)
        ):
            turn, _ = play_player_turn(1, player, bust_index=1)
        self.assertEqual(turn["ctl"], 7)
        self.assertEqual(turn["fatigue_turn"], energy_and_fatigue(7, 20)[1])
        self.assertEqual(player.progress.quality_total, 0)


if __name__ == "__main__":
    unittest.main()
