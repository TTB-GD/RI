"""Explicit player dice actions for Training B."""
import unittest
import random

from training_v2 import (
    PlayerState, RollResult, SessionAllocation, resolve_dice_action,
    roll_pool, roll_and_resolve_turn, list_program_options, resolve_turn,
)


class TrainingBDiceActionTests(unittest.TestCase):
    def setUp(self):
        self.roll = RollResult(
            raw_faces=(2, 3, 4, 5),
            final_values=(2, 3, 4),
            tn=14.0,
            active_sizes=(6, 6, 6),
            reserve_index=3,
            reserve_value=5,
            reserve_size=6,
        )

    def test_keep_uses_only_initial_active_dice(self):
        result = resolve_dice_action(self.roll, "keep")
        self.assertEqual(result.final_values, (2, 3, 4))
        self.assertEqual(result.energy, 9)

    def test_add_uses_the_rolled_reserve(self):
        result = resolve_dice_action(self.roll, "add")
        self.assertEqual(result.final_values, (2, 3, 4, 5))
        self.assertEqual(result.energy, 14)

    def test_reroll_replaces_one_active_die(self):
        result = resolve_dice_action(
            self.roll, "reroll", reroll_index=1, rerolled_value=6
        )
        self.assertEqual(result.final_values, (2, 6, 4))
        self.assertEqual(result.energy, 12)

    def test_add_and_reroll_can_be_combined(self):
        result = resolve_dice_action(
            self.roll, "add+reroll", reroll_index=1, rerolled_value=6
        )
        self.assertEqual(result.final_values, (2, 6, 4, 5))
        self.assertEqual(result.energy, 17)

    def test_overtraining_blocks_only_reserve_actions(self):
        with self.assertRaises(ValueError):
            resolve_dice_action(self.roll, "add", overtraining=True)
        reroll = resolve_dice_action(
            self.roll, "reroll", reroll_index=0, rerolled_value=6,
            overtraining=True,
        )
        self.assertEqual(reroll.final_values, (6, 3, 4))

    def test_initial_roll_keeps_reserve_separate_but_includes_it_in_tn(self):
        state = PlayerState()
        roll = roll_pool(state, rng=random.Random(7))
        self.assertEqual(len(roll.raw_faces), 4)
        self.assertEqual(len(roll.active_values), 3)
        self.assertEqual(roll.tn, 14.0)
        self.assertEqual(roll.reserve_size, 6)

    def test_turn_pipeline_applies_action_before_session_allocation(self):
        state = PlayerState()
        result = roll_and_resolve_turn(
            state,
            lambda dice: list_program_options(state, dice)[0].allocations,
            choose_dice_action=lambda roll: "add",
            rng=random.Random(3),
        )
        self.assertEqual(result.dice_action, "add")
        self.assertEqual(len(result.final_values), 4)

    def test_blackjack_fatigue_survives_a_busted_session(self):
        state = PlayerState()
        allocation = (
            SessionAllocation("VMA", (0, 1, 2, 3), 16),
        )
        result = resolve_turn(
            state, (4, 4, 4, 4), allocation, risk_faces=(1,),
            final_values_override=(4, 4, 4, 4), dice_action="add",
        )
        self.assertEqual(result.busted_session, "VMA")
        self.assertGreater(result.fatigue_blackjack, 0)
        self.assertEqual(result.fatigue_specific, 0)
        self.assertGreaterEqual(state.fatigue, result.fatigue_blackjack)


if __name__ == "__main__":
    unittest.main()
