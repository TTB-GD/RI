"""Integration invariants for injected Training RNG and delayed progression."""

import unittest
from unittest.mock import patch

from dice_progression import PlayerDicePool
from player_state import Player
from simulate_player import play_player_turn


class ScriptedRNG:
    def __init__(self, faces):
        self.faces = iter(faces)
        self.calls = []

    def randint(self, low, high):
        self.calls.append((low, high))
        face = next(self.faces)
        if not low <= face <= high:
            raise AssertionError(f"scripted face {face} outside [{low}, {high}]")
        return face


class TrainingTurnRNGIntegrationTests(unittest.TestCase):
    def test_same_rng_is_used_for_risk_after_budget_roll(self):
        player = Player(dice_pool=PlayerDicePool(sizes=[6, 6, 6, 6]))
        accessible = ["EF1", "Seuil5"]
        player.progress.available_sessions = lambda: accessible
        player.progress.tentable_sessions = lambda: accessible
        budget = {
            "energy_budget": 10, "rpe_max": 4, "quality_sessions_from_roll": 1,
            "tn": 14, "pool_size": 4, "final_faces": [2, 2, 2],
            "final_values": [2, 2, 2], "pattern": "test", "action_chosen": "keep",
        }
        plan = ["EF1", "Seuil5"]
        trace = [{"session": name, "note": "test"} for name in plan]
        rng = ScriptedRNG([2])

        with patch("simulate_player.roll_turn_budget", return_value=budget), patch(
            "simulate_player.choose_sessions_weighted", return_value=(plan, trace)
        ):
            turn, _ = play_player_turn(1, player, rng=rng)

        self.assertEqual(rng.calls, [(1, 6)])
        self.assertEqual(turn["sessions_completed"], "EF1")
        self.assertEqual(turn["energy_lost"], 5)


class QualityUpgradeTransitionTests(unittest.TestCase):
    def test_upgrade_unlocked_by_fourth_quality_applies_next_turn(self):
        player = Player(dice_pool=PlayerDicePool(), cumulative_ctl=0)
        player.progress.quality_total = 3
        accessible = ["EF1", "Seuil3"]
        player.progress.available_sessions = lambda: accessible
        player.progress.tentable_sessions = lambda: accessible
        roll = {
            "energy_budget": 10, "rpe_max": 4, "quality_sessions_from_roll": 1,
            "tn": 14, "pool_size": 4, "final_faces": [2, 2, 2],
            "final_values": [2, 2, 2], "pattern": "test", "action_chosen": "keep",
        }
        planned_quality = (["EF1", "Seuil3"], [
            {"session": "EF1", "note": "test"},
            {"session": "Seuil3", "note": "test"},
        ])

        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted", return_value=planned_quality
        ):
            first_turn, _ = play_player_turn(1, player)
        self.assertEqual(first_turn["upgrades_used"], 0)
        self.assertEqual(player.progress.quality_total, 4)
        self.assertEqual(player.dice_pool.sizes, [6, 6, 6, 6])

        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted", return_value=([], [])
        ):
            second_turn, _ = play_player_turn(2, player)
        self.assertEqual(second_turn["upgrades_used"], 1)
        self.assertEqual(player.dice_pool.sizes, [8, 6, 6, 6])


if __name__ == "__main__":
    unittest.main()
