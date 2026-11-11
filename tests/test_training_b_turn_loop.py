"""Main Training B dice-to-budget turn loop."""
import random
import unittest

from training_v2 import PlayerState, TrainingEnergyBudget
from training_v2.dice import roll_initial, resolve_dice_action
from training_v2.turn import resolve_training_turn


class CountingRng:
    def __init__(self, values):
        self.values = iter(values)
        self.calls = 0

    def randint(self, low, high):
        self.calls += 1
        value = next(self.values)
        if not low <= value <= high:
            raise AssertionError("fixed die result outside requested range")
        return value


class TrainingBTurnLoopTests(unittest.TestCase):
    def test_initial_roll_rolls_exactly_n_minus_one_dice(self):
        rng = CountingRng((2, 3, 4, 5))
        roll = roll_initial([6, 6, 6, 6], rng=rng, defer_reserve=True)
        self.assertEqual(rng.calls, 3)
        self.assertEqual(roll.final_values, (2, 3, 4))
        self.assertIsNone(roll.reserve_value)
        self.assertIsNone(roll.raw_faces[3])
        self.assertEqual(roll.tn, 14.0)

    def test_keep_does_not_roll_reserve(self):
        rng = CountingRng((2, 3, 4))
        roll = roll_initial([6, 6, 6, 6], rng=rng, defer_reserve=True)
        result = resolve_dice_action(roll, "keep", rng=rng)
        self.assertEqual(rng.calls, 3)
        self.assertEqual(result.final_values, (2, 3, 4))
        self.assertIsNone(result.raw_faces[3])

    def test_add_rolls_reserve_only_after_player_choice(self):
        rng = CountingRng((2, 3, 4, 5))
        roll = roll_initial([6, 6, 6, 6], rng=rng, defer_reserve=True)
        self.assertEqual(rng.calls, 3)
        result = resolve_dice_action(roll, "add", rng=rng)
        self.assertEqual(rng.calls, 4)
        self.assertEqual(result.final_values, (2, 3, 4, 5))
        self.assertEqual(result.raw_faces, (2, 3, 4, 5))

    def test_add_and_reroll_rolls_reserve_after_reroll(self):
        rng = CountingRng((2, 3, 4, 6, 5))
        roll = roll_initial([6, 6, 6, 6], rng=rng, defer_reserve=True)
        result = resolve_dice_action(
            roll, "add+reroll", reroll_index=1, rng=rng,
        )
        self.assertEqual(rng.calls, 5)
        self.assertEqual(result.final_values, (2, 6, 4, 5))

    def test_turn_loop_conserves_energy_and_applies_dice_fatigue(self):
        rng = CountingRng((4, 4, 4, 4))
        state = PlayerState()
        result = resolve_training_turn(
            state,
            choose_dice_action=lambda roll: "add",
            allocate_budget=lambda dice: TrainingEnergyBudget(
                total_energy=dice.energy,
                ef_energy=4,
                threshold_energy=6,
                vma_energy=6,
            ),
            rng=rng,
        )
        self.assertEqual(result.dice.energy, 16)
        self.assertEqual(result.budget.total_energy, 16)
        self.assertEqual(result.fatigue_delta, 5)
        self.assertEqual(state.fatigue, 5)
        self.assertEqual(state.turns_played, 1)

    def test_invalid_budget_does_not_mutate_player_state(self):
        state = PlayerState()
        with self.assertRaisesRegex(ValueError, "must equal"):
            resolve_training_turn(
                state,
                choose_dice_action=lambda roll: "keep",
                allocate_budget=lambda dice: TrainingEnergyBudget(
                    total_energy=dice.energy + 1,
                    ef_energy=dice.energy + 1,
                    threshold_energy=0,
                    vma_energy=0,
                ),
                rng=random.Random(4),
            )
        self.assertEqual(state.fatigue, 0)
        self.assertEqual(state.turns_played, 0)

    def test_overtraining_still_allows_reroll_but_blocks_add(self):
        state = PlayerState()
        with self.assertRaisesRegex(ValueError, "reserve actions"):
            resolve_training_turn(
                state,
                choose_dice_action=lambda roll: "add",
                allocate_budget=lambda dice: TrainingEnergyBudget(
                    dice.energy, dice.energy, 0, 0
                ),
                rng=random.Random(4),
                overtraining=True,
            )
        result = resolve_training_turn(
            state,
            choose_dice_action=lambda roll: ("reroll", 0),
            allocate_budget=lambda dice: TrainingEnergyBudget(
                dice.energy, dice.energy, 0, 0
            ),
            rng=random.Random(4),
            overtraining=True,
        )
        self.assertEqual(result.dice.action, "reroll")


if __name__ == "__main__":
    unittest.main()
