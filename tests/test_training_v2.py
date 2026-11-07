"""Focused tests for the isolated Training V2 first playable turn."""
import unittest

from training_v2 import (
    PlayerState, PhysiologyProfile, RollResult, list_program_options, resolve_turn,
)
from training_v2.catalog import QUALITY_CATALOG, QualityOption, quality_cost


class TrainingV2TurnTests(unittest.TestCase):
    def test_profile_requires_ordered_landmarks(self):
        with self.assertRaises(ValueError):
            PhysiologyProfile(ef=8, threshold=8, vma=10).validate()

    def test_catalogue_declares_session_family_load_and_adaptations(self):
        seuil = QUALITY_CATALOG["SEUIL"]
        vma = QUALITY_CATALOG["VMA"]
        self.assertEqual((seuil.family, seuil.load_type), ("SEUIL", "QUALITY"))
        self.assertEqual(seuil.adaptations, (("threshold", 1),))
        self.assertEqual(vma.adaptations, (("vma", 1),))
        self.assertEqual((seuil.energy_cost, seuil.rpe), (4, 4))
        self.assertEqual((vma.energy_cost, vma.rpe), (5, 5))
        self.assertEqual(vma.fatigue, 1)
        self.assertEqual(seuil.max_per_turn, 1)

    def test_catalogue_rejects_invalid_load_type(self):
        with self.assertRaises(ValueError):
            QualityOption(
                key="BAD", label="Bad", profile_attribute="vma",
                family="VMA", load_type="OTHER",
            )

    def test_historical_b2_cost_formula_remains_available_for_reference(self):
        self.assertEqual(quality_cost(8, 6), 3)
        self.assertEqual(quality_cost(12, 6), 7)
        self.assertEqual(quality_cost(13, 6), 9)

    def test_risk_uses_rpe_not_energy_cost(self):
        from unittest.mock import patch

        state = PlayerState()
        option = QualityOption(
            key="TEST", label="Test", profile_attribute="threshold",
            family="SEUIL", adaptations=(("threshold", 1),),
            energy_cost=1, rpe=6,
        )
        with patch.dict(QUALITY_CATALOG, {"TEST": option}):
            result = resolve_turn(
                state, (2, 2, 2, 2),
                ef_indices=(0, 1), quality_indices=(2, 3),
                planned_qualities=("TEST",), risk_faces=(1,),
            )
        self.assertEqual(result.quality_costs, (("TEST", 1),))
        self.assertEqual(result.busted_quality, "TEST")

    def test_energy_cost_is_not_used_as_rpe(self):
        from unittest.mock import patch

        state = PlayerState()
        option = QualityOption(
            key="TEST", label="Test", profile_attribute="threshold",
            family="SEUIL", adaptations=(("threshold", 1),),
            energy_cost=6, rpe=1,
        )
        with patch.dict(QUALITY_CATALOG, {"TEST": option}):
            result = resolve_turn(
                state, (3, 3, 3, 3),
                ef_indices=(0, 1), quality_indices=(2, 3),
                planned_qualities=("TEST",),
            )
        self.assertEqual(result.quality_costs, (("TEST", 6),))
        self.assertIsNone(result.busted_quality)

    def test_multidimensional_catalogue_adaptation_is_applied_generically(self):
        from unittest.mock import patch

        state = PlayerState()
        state.progression_ef = 150
        state.ef_milestones_claimed = {10, 20, 35, 50, 70, 100, 120, 150}
        multidimensional = QualityOption(
            key="TEST", label="Test", profile_attribute="threshold",
            family="SEUIL", adaptations=(("threshold", 1), ("ef", 1)),
        )
        with patch.dict(QUALITY_CATALOG, {"TEST": multidimensional}):
            result = resolve_turn(
                state, (6, 6, 6, 6),
                ef_indices=(0, 1), quality_indices=(2, 3),
                planned_qualities=("TEST",),
            )
        self.assertEqual(result.successful_qualities, ("TEST",))
        self.assertEqual(state.profile.threshold, 9)
        self.assertEqual(state.profile.ef, 7)

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
        # EF milestones 10 and 20 are both crossed over the two turns.
        self.assertEqual(state.profile.ef, 8)
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

    def test_program_options_include_multi_quality_choice_without_ranking(self):
        state = PlayerState()
        roll = RollResult(
            raw_faces=(6, 6, 6, 6), final_values=(6, 6, 6, 6), tn=14.0
        )
        options = list_program_options(state, roll)
        both = next(
            option for option in options
            if option.ef_indices == (0, 1)
            and option.quality_indices == (2, 3)
            and option.qualities == ("SEUIL", "VMA")
        )
        self.assertEqual(both.ef_energy, 12)
        self.assertEqual(both.quality_energy, 12)
        self.assertEqual(both.quality_costs, (("SEUIL", 4), ("VMA", 5)))
        self.assertEqual(both.spec_remainder, 3)
        self.assertGreater(len(options), 1)

    def test_program_options_include_quality_to_spec_without_session(self):
        state = PlayerState()
        roll = RollResult(
            raw_faces=(6, 6, 1, 1), final_values=(6, 6, 1, 1), tn=14.0
        )
        options = list_program_options(state, roll)
        no_quality = next(
            option for option in options
            if option.quality_indices == (2, 3) and not option.qualities
        )
        self.assertEqual(no_quality.quality_energy, 2)
        self.assertEqual(no_quality.spec_remainder, 2)

    def test_program_options_accept_roll_with_lowest_die_discarded(self):
        state = PlayerState()
        roll = RollResult(
            raw_faces=(1, 2, 3, 4), final_values=(4, 3, 2), tn=14.0
        )
        options = list_program_options(state, roll)
        self.assertTrue(options)
        self.assertTrue(all(
            max(option.ef_indices + option.quality_indices) < 3
            for option in options
        ))

    def test_program_options_reject_pool_mismatch(self):
        state = PlayerState()
        roll = RollResult(raw_faces=(6, 6), final_values=(6, 6), tn=14.0)
        with self.assertRaises(ValueError):
            list_program_options(state, roll)

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
        self.assertEqual(state.progression_spec, 0)

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
