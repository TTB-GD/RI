"""Tests for direct dice-to-session allocation in Training B."""
import unittest
from unittest.mock import patch

from training_v2 import (
    PlayerState, PhysiologyProfile, RollResult, SessionAllocation,
    list_program_options, resolve_turn, make_session_eligible, acquire_session,
)
from training_v2.catalog import SESSION_CATALOG, SessionOption, quality_cost


class TrainingBAllocationTests(unittest.TestCase):
    def test_profile_requires_ordered_landmarks(self):
        with self.assertRaises(ValueError):
            PhysiologyProfile(ef=8, threshold=8, vma=10).validate()

    def test_catalogue_has_initial_ef_threshold_vma_sessions(self):
        self.assertEqual(set(SESSION_CATALOG), {"EF", "SEUIL", "VMA"})
        self.assertEqual(SESSION_CATALOG["EF"].load_type, "EF")
        self.assertIsNone(SESSION_CATALOG["EF"].max_per_turn)
        self.assertEqual(SESSION_CATALOG["SEUIL"].energy_cost, 4)
        self.assertEqual(SESSION_CATALOG["VMA"].rpe, 5)

    def test_eligibility_does_not_automatically_acquire_session(self):
        state = PlayerState()
        self.assertNotIn("INTERVALLES_COURTS", state.acquired_session_keys)
        make_session_eligible(state, "INTERVALLES_COURTS")
        self.assertIn("INTERVALLES_COURTS", state.eligible_session_keys)
        self.assertNotIn("INTERVALLES_COURTS", state.acquired_session_keys)

    def test_only_acquired_sessions_are_enumerated_and_playable(self):
        state = PlayerState()
        roll = RollResult((6, 6, 6, 6), (6, 6, 6, 6), 14.0)
        initial = list_program_options(state, roll)
        self.assertFalse(any(
            item.session_key == "INTERVALLES_COURTS"
            for option in initial for item in option.allocations
        ))

        make_session_eligible(state, "INTERVALLES_COURTS")
        acquire_session(state, "INTERVALLES_COURTS")
        options = list_program_options(state, roll)
        self.assertTrue(any(
            item.session_key == "INTERVALLES_COURTS"
            for option in options for item in option.allocations
        ))

        allocation = (SessionAllocation("INTERVALLES_COURTS", (0, 1, 2, 3), 24),)
        result = resolve_turn(state, (6, 6, 6, 6), allocation)
        self.assertEqual(result.successful_sessions, allocation)
        self.assertEqual(state.profile.vma, 13)

    def test_ineligible_session_cannot_be_acquired(self):
        state = PlayerState()
        with self.assertRaises(ValueError):
            acquire_session(state, "INTERVALLES_COURTS")

    def test_unknown_session_cannot_be_unlocked(self):
        state = PlayerState()
        with self.assertRaises(ValueError):
            make_session_eligible(state, "NOT_IN_CATALOGUE")

    def test_clone_copies_portfolio_sets_independently(self):
        state = PlayerState()
        make_session_eligible(state, "INTERVALLES_COURTS")
        clone = state.clone()
        acquire_session(clone, "INTERVALLES_COURTS")
        self.assertNotIn("INTERVALLES_COURTS", state.acquired_session_keys)
        self.assertIn("INTERVALLES_COURTS", clone.acquired_session_keys)

    def test_catalogue_rejects_invalid_load_type(self):
        with self.assertRaises(ValueError):
            SessionOption(
                key="BAD", label="Bad", family="VMA", load_type="OTHER",
                adaptations=(("vma", 1),), energy_cost=1, rpe=1,
            )

    def test_historical_b2_cost_formula_is_not_active(self):
        self.assertEqual(quality_cost(8, 6), 3)

    def test_options_allocate_every_die_once_without_ef_q_partition(self):
        state = PlayerState()
        roll = RollResult((6, 6, 6, 6), (6, 6, 6, 6), 14.0)
        options = list_program_options(state, roll)
        self.assertTrue(options)
        for option in options:
            indices = [i for item in option.allocations for i in item.die_indices]
            self.assertEqual(sorted(indices), [0, 1, 2, 3])
        self.assertTrue(any(
            any(item.session_key == "EF" for item in option.allocations)
            and any(item.session_key == "SEUIL" for item in option.allocations)
            for option in options
        ))

    def test_ef_sessions_can_repeat_and_quality_sessions_are_limited(self):
        state = PlayerState()
        roll = RollResult((6, 6, 6, 6), (6, 6, 6, 6), 14.0)
        options = list_program_options(state, roll)
        self.assertTrue(any(
            sum(item.session_key == "EF" for item in option.allocations) == 2
            for option in options
        ))
        self.assertFalse(any(
            sum(item.session_key == "SEUIL" for item in option.allocations) > 1
            for option in options
        ))

    def test_equivalent_die_permutations_are_collapsed(self):
        state = PlayerState(dice_pool=[6, 6, 6, 6, 6, 6])
        roll = RollResult((6, 6, 6, 6, 6, 6), (6, 6, 6, 6, 6, 6), 21.0)
        options = list_program_options(state, roll)
        self.assertGreater(len(options), 0)
        self.assertLess(len(options), 100)

    def test_ef_only_composition_is_available(self):
        state = PlayerState()
        roll = RollResult((6, 6, 6, 6), (6, 6, 6, 6), 14.0)
        options = list_program_options(state, roll)
        self.assertTrue(any(
            all(item.session_key == "EF" for item in option.allocations)
            for option in options
        ))

    def test_resolve_applies_session_adaptation_and_tracks_load(self):
        state = PlayerState()
        allocation = (SessionAllocation("SEUIL", (0, 1), 12),
                      SessionAllocation("EF", (2, 3), 12))
        result = resolve_turn(state, (6, 6, 6, 6), allocation)
        self.assertEqual([x.session_key for x in result.successful_sessions],
                         ["SEUIL", "EF"])
        self.assertEqual(state.profile.threshold, 9)
        self.assertEqual(state.profile.ef, 7)
        self.assertEqual(state.progression_ef, 12)
        self.assertEqual(state.progression_q, 4)

    def test_bust_prevents_session_adaptation(self):
        state = PlayerState()
        allocation = (SessionAllocation("SEUIL", (0, 1), 4),
                      SessionAllocation("EF", (2, 3), 4))
        # RPE 4 > retained max 2; risk face 1 busts the first session.
        result = resolve_turn(state, (2, 2, 2, 2), allocation, risk_faces=(1,))
        self.assertEqual(result.busted_session, "SEUIL")
        self.assertEqual(state.profile.threshold, 8)
        self.assertEqual(state.progression_q, 0)

    def test_busted_quality_does_not_count_as_realized_load_or_spec(self):
        state = PlayerState()
        allocation = (
            SessionAllocation("EF", (0,), 2),
            SessionAllocation("VMA", (1, 2, 3), 6),
        )
        # EF completes; VMA is risky and busts. Its unused Quality remainder
        # and its planned energy must not affect realized progression or load.
        result = resolve_turn(state, (2, 2, 2, 2), allocation, risk_faces=(1,))
        self.assertEqual([x.session_key for x in result.successful_sessions], ["EF"])
        self.assertEqual(result.busted_session, "VMA")
        self.assertEqual(result.ef_energy, 2)
        self.assertEqual(result.quality_energy, 0)
        self.assertEqual(result.progression_spec_gained, 0)
        self.assertEqual(state.progression_spec, 0)
        self.assertEqual(result.fatigue_excess, 0)

    def test_invalid_allocation_does_not_mutate_state(self):
        state = PlayerState()
        before = state.clone()
        invalid = (SessionAllocation("SEUIL", (0, 1), 12),)
        with self.assertRaises(ValueError):
            resolve_turn(state, (6, 6, 6, 6), invalid)
        self.assertEqual(state, before)

    def test_unknown_session_is_rejected(self):
        state = PlayerState()
        with self.assertRaises(ValueError):
            resolve_turn(state, (6, 6, 6, 6),
                         (SessionAllocation("UNKNOWN", (0, 1, 2, 3), 24),))

    def test_profile_order_is_checked_before_mutation(self):
        state = PlayerState(profile=PhysiologyProfile(ef=6, threshold=9, vma=10))
        invalid = (SessionAllocation("SEUIL", (0, 1, 2, 3), 24),)
        before = state.clone()
        with self.assertRaises(ValueError):
            resolve_turn(state, (6, 6, 6, 6), invalid)
        self.assertEqual(state, before)

    def test_roll_and_resolve_uses_direct_allocations(self):
        from training_v2 import roll_and_resolve_turn
        state = PlayerState()
        result = roll_and_resolve_turn(
            state,
            lambda roll: list_program_options(state, roll)[0].allocations,
            rng=__import__("random").Random(3),
        )
        self.assertEqual(result.turn, 1)
        self.assertEqual(state.turns_played, 1)


if __name__ == "__main__":
    unittest.main()
