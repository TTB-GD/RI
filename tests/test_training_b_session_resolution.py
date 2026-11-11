import unittest

from training_v2.budget import TrainingEnergyBudget
from training_v2.session_resolution import SESSION_DOSES, resolve_session_plan
from training_v2.state import PlayerState


class TrainingBSessionResolutionTests(unittest.TestCase):
    def budget(self, ef=0, threshold=0, vma=0):
        return TrainingEnergyBudget(ef + threshold + vma, ef, threshold, vma)

    def test_catalog_contains_exact_nine_dose_entries(self):
        self.assertEqual(set(SESSION_DOSES), {
            "EF1", "EF2", "EF3", "EF4",
            "SEUIL3", "SEUIL4", "SEUIL5",
            "VMA3", "VMA4", "VMA5",
        })
        for key, session in SESSION_DOSES.items():
            self.assertEqual(session.calibration, "EXPERIMENTAL")
            self.assertEqual(session.dose, int(key[-1]))

    def test_resolves_both_quality_filiers_and_applies_independent_xp(self):
        state = PlayerState()
        result = resolve_session_plan(
            state, self.budget(ef=2, threshold=3, vma=4),
            ("EF2", "SEUIL3", "VMA4"), rpe_authorized=6,
        )
        self.assertIsNone(result.busted_session)
        self.assertEqual(result.successful_sessions, ("EF2", "SEUIL3", "VMA4"))
        self.assertEqual(state.progression_ef, 2)
        self.assertEqual(state.progression_threshold, 3)
        self.assertEqual(state.progression_vma, 3)
        self.assertEqual(state.fatigue, 7)

    def test_first_bust_cancels_current_and_later_effects_but_keeps_prior(self):
        state = PlayerState(fatigue=3)
        faces = iter((2,))
        result = resolve_session_plan(
            state, self.budget(ef=1, threshold=3, vma=3),
            ("EF1", "SEUIL3", "VMA3"), rpe_authorized=2,
            risk_roll=lambda size: next(faces),
        )
        self.assertEqual(result.busted_session, "SEUIL3")
        self.assertEqual(result.cancelled_sessions, ("VMA3",))
        self.assertEqual(result.successful_sessions, ("EF1",))
        self.assertEqual(state.progression_ef, 1)
        self.assertEqual(state.progression_threshold, 0)
        self.assertEqual(state.progression_vma, 0)
        self.assertEqual(state.fatigue, 3)

    def test_bust_keeps_dice_fatigue_already_on_state(self):
        state = PlayerState(fatigue=7)
        result = resolve_session_plan(
            state, self.budget(threshold=3), ("SEUIL3",),
            rpe_authorized=1, risk_roll=lambda size: 1,
        )
        self.assertIsNotNone(result.busted_session)
        self.assertEqual(state.fatigue, 7)

    def test_rejects_budget_mismatch(self):
        with self.assertRaisesRegex(ValueError, "do not match budgets"):
            resolve_session_plan(
                PlayerState(), self.budget(ef=3), ("EF2",), rpe_authorized=4,
            )

    def test_rejects_repeated_quality_entry(self):
        with self.assertRaisesRegex(ValueError, "repetition limit"):
            resolve_session_plan(
                PlayerState(), self.budget(threshold=6),
                ("SEUIL3", "SEUIL3"), rpe_authorized=5,
            )

    def test_rejects_session_not_in_portfolio(self):
        state = PlayerState()
        state.acquired_session_keys.remove("EF1")
        with self.assertRaisesRegex(ValueError, "not acquired"):
            resolve_session_plan(
                state, self.budget(ef=1), ("EF1",), rpe_authorized=4,
            )


if __name__ == "__main__":
    unittest.main()
