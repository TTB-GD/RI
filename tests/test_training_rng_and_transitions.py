"""Deterministic RNG and longitudinal Training progression regressions."""

import random
import unittest
from unittest.mock import patch

from dice_progression import PlayerDicePool
from dice_types import Die
from player_state import Player
from session_risk import first_bust_index
from simulate_player import roll_turn_budget, run_player_simulation


class InjectedRNGTests(unittest.TestCase):
    def test_die_roll_replays_from_equal_rng_seeds(self):
        self.assertEqual(Die(10).roll(random.Random(1234)),
                         Die(10).roll(random.Random(1234)))

    def test_risk_roll_replays_from_injected_rng(self):
        result_a = first_bust_index(["Seuil5"], 4, [6], rng=random.Random(1))
        result_b = first_bust_index(["Seuil5"], 4, [6], rng=random.Random(1))
        self.assertEqual(result_a, result_b)

    def test_roll_turn_budget_replays_from_equal_rng_seeds(self):
        pool_a = PlayerDicePool(sizes=[6, 6, 8, 10])
        pool_b = PlayerDicePool(sizes=[6, 6, 8, 10])
        self.assertEqual(
            roll_turn_budget(pool_a, rng=random.Random(876)),
            roll_turn_budget(pool_b, rng=random.Random(876)),
        )

    def test_simulation_seed_replays_and_does_not_mutate_global_rng(self):
        global_rng = random.getstate()
        first = run_player_simulation(n_turns=2, seed=2718)
        self.assertEqual(random.getstate(), global_rng)
        second = run_player_simulation(n_turns=2, seed=2718)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        self.assertEqual(first[2], second[2])


class LongitudinalProgressionTests(unittest.TestCase):
    def test_ctl_milestones_add_one_d6_once_each(self):
        pool = PlayerDicePool()
        original = list(pool.sizes)

        pool.maybe_add_dice(49)
        self.assertEqual(pool.sizes, original)
        pool.maybe_add_dice(50)
        self.assertEqual(pool.sizes, original + [6])
        pool.maybe_add_dice(99)
        pool.maybe_add_dice(100)
        self.assertEqual(pool.sizes, original + [6, 6])
        pool.maybe_add_dice(150)
        self.assertEqual(pool.sizes, original + [6, 6])
        self.assertEqual(pool.dice_added, 2)

    def test_quality_upgrades_are_thresholded_capped_and_idempotent(self):
        pool = PlayerDicePool()
        pool.maybe_upgrade(3)
        self.assertEqual(pool.sizes, [6, 6, 6, 6])
        self.assertEqual(pool.upgrades_used, 0)

        pool.maybe_upgrade(4)
        self.assertEqual(pool.sizes, [8, 6, 6, 6])
        self.assertEqual(pool.upgrades_used, 1)
        pool.maybe_upgrade(4)
        self.assertEqual(pool.upgrades_used, 1)

        pool.maybe_upgrade(20)
        self.assertEqual(pool.upgrades_used, 4)
        self.assertEqual(pool.sizes, [8, 8, 8, 8])
        pool.maybe_upgrade(100)
        self.assertEqual(pool.upgrades_used, 4)

    def test_threshold_gains_take_effect_at_start_of_following_turn(self):
        player = Player(dice_pool=PlayerDicePool(), cumulative_ctl=49)
        roll = {
            "energy_budget": 1, "rpe_max": 1, "quality_sessions_from_roll": 0,
            "tn": 20, "pool_size": 4, "final_faces": [1, 1, 1],
            "final_values": [1, 1, 1], "pattern": "test", "action_chosen": "keep",
        }
        available = ["EF1"]
        player.progress.available_sessions = lambda: available
        player.progress.tentable_sessions = lambda: available

        with patch("simulate_player.roll_turn_budget", return_value=roll), patch(
            "simulate_player.choose_sessions_weighted",
            return_value=(["EF1"], [{"session": "EF1", "note": "test"}]),
        ):
            first_turn, _ = __import__("simulate_player").play_player_turn(1, player)
            self.assertEqual(first_turn["dice_pool_sizes"], "6-6-6-6")
            self.assertEqual(first_turn["cumulative_ctl"], 50)

            second_roll = dict(roll, pool_size=5)
            with patch("simulate_player.roll_turn_budget", return_value=second_roll):
                second_turn, _ = __import__("simulate_player").play_player_turn(2, player)

        self.assertEqual(second_turn["dice_pool_sizes"], "6-6-6-6-6")
        self.assertEqual(player.dice_pool.dice_added, 1)


if __name__ == "__main__":
    unittest.main()
