"""Focused tests for the isolated Training V2 first playable turn."""
import unittest

from training_v2 import PlayerState, PhysiologyProfile, resolve_turn
from training_v2.catalog import quality_cost


class TrainingV2TurnTests(unittest.TestCase):
    def test_profile_requires_ordered_landmarks(self):
        with self.assertRaises(ValueError):
            PhysiologyProfile(ef=8, threshold=8, vma=10).validate()

    def test_quality_cost_matches_b2_boundary(self):
        self.assertEqual(quality_cost(8, 6), 3)
        self.assertEqual(quality_cost(12, 6), 7)
        self.assertEqual(quality_cost(13, 6), 9)

    def test_successful_quality_updates_profile_and_persists(self):
        state = PlayerState()
        result = resolve_turn(
            state, (6, 6, 6, 6),
            ef_indices=(0, 1), quality_indices=(2, 3),
            planned_qualities=("SEUIL",),
        )
        self.assertEqual(result.ef_energy, 12)
        self.assertEqual(result.quality_energy, 12)
        self.assertEqual(result.successful_qualities, ("SEUIL",))
        self.assertEqual(state.profile.threshold, 9)
        self.assertEqual(state.turns_played, 1)
        self.assertEqual(state.progression_ef, 12)
        self.assertEqual(state.progression_q, 3)
        self.assertEqual(state.progression_spec, 9)

    def test_two_turns_reuse_the_updated_player_state(self):
        state = PlayerState()
        first = resolve_turn(
            state, (6, 6, 6, 6),
            ef_indices=(0, 1), quality_indices=(2, 3),
            planned_qualities=("SEUIL",),
        )
        second = resolve_turn(
            state, (6, 6, 6, 6),
            ef_indices=(0, 1), quality_indices=(2, 3),
            planned_qualities=("VMA",),
        )
        self.assertEqual((first.turn, second.turn), (1, 2))
        self.assertEqual(state.profile.ef, 7)
        self.assertEqual(state.profile.threshold, 9)
        self.assertEqual(state.profile.vma, 11)
        self.assertEqual(state.turns_played, 2)

    def test_roll_and_resolve_callback_selects_after_the_roll(self):
        from training_v2 import roll_and_resolve_turn

        state = PlayerState()

        def choose_program(roll):
            quality_index = min(
                range(len(roll.final_values)),
                key=lambda index: roll.final_values[index],
            )
            ef_indices = tuple(
                index for index in range(len(roll.final_values))
                if index != quality_index
            )
            return ef_indices, (quality_index,), ()

        result = roll_and_resolve_turn(
            state, choose_program, rng=__import__("random").Random(3)
        )
        self.assertEqual(result.turn, 1)
        self.assertEqual(state.turns_played, 1)

    def test_bust_loses_assigned_quality_energy_and_does_not_adapt(self):
        state = PlayerState()
        result = resolve_turn(
            state, (2, 2, 2, 2),
            ef_indices=(0, 1), quality_indices=(2, 3),
            planned_qualities=("SEUIL",), risk_faces=(1,),
        )
        self.assertEqual(result.busted_quality, "SEUIL")
        self.assertEqual(result.successful_qualities, ())
        self.assertEqual(state.profile.threshold, 8)
        self.assertEqual(state.progression_q, 0)
        self.assertEqual(state.progression_spec, 9)

    def test_invalid_partition_is_rejected_without_mutating_state(self):
        state = PlayerState()
        before = state.clone()
        with self.assertRaises(ValueError):
            resolve_turn(
                state, (6, 6, 6, 6),
                ef_indices=(0,), quality_indices=(1, 2, 3),
                planned_qualities=("SEUIL", "VMA"),
            )
        self.assertEqual(state, before)

    def test_quality_program_must_fit_allocated_compartment(self):
        state = PlayerState()
        before = state.clone()
        with self.assertRaises(ValueError):
            resolve_turn(
                state, (6, 6, 6, 6),
                ef_indices=(0, 1, 2), quality_indices=(3,),
                planned_qualities=("SEUIL", "VMA"),
            )
        self.assertEqual(state, before)

    def test_milestone_adds_dice_and_upgrade_once(self):
        state = PlayerState()
        state.progression_ef = 34
        state.progression_q = 14
        resolve_turn(
            state, (6, 6, 6, 6),
            ef_indices=(0, 1), quality_indices=(2, 3),
            planned_qualities=("SEUIL",),
        )
        self.assertEqual(len(state.dice_pool), 5)
        self.assertEqual(state.dice_added, 1)
        self.assertEqual(state.upgrades_used, 1)
        self.assertEqual(state.profile.ef, 6)


if __name__ == "__main__":
    unittest.main()
