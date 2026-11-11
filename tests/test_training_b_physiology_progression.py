import unittest

from training_v2 import (
    PlayerState, PhysiologyPoint, PhysiologyCurve, PhysiologyMilestone,
    TrainingEnergyBudget, apply_physiology_milestones, resolve_session_plan,
)


def curve():
    return PhysiologyCurve(
        ef=PhysiologyPoint(energy=6, speed=10),
        threshold=PhysiologyPoint(energy=8, speed=12),
        vma=PhysiologyPoint(energy=10, speed=14),
    )


class PhysiologyCurveTests(unittest.TestCase):
    def test_profile_orders_both_energy_and_speed_coordinates(self):
        with self.assertRaises(ValueError):
            PhysiologyCurve(
                PhysiologyPoint(6, 10), PhysiologyPoint(8, 9), PhysiologyPoint(10, 14)
            )
        with self.assertRaises(ValueError):
            PhysiologyCurve(
                PhysiologyPoint(6, 10), PhysiologyPoint(7, 12), PhysiologyPoint(7, 14)
            )

    def test_vma_energy_is_race_spend_ceiling(self):
        self.assertEqual(curve().max_race_energy, 10)

    def test_speed_choice_changes_speed_only(self):
        upgraded = curve().upgraded("threshold", "speed", 0.5)
        self.assertEqual(upgraded.threshold.energy, 8)
        self.assertEqual(upgraded.threshold.speed, 12.5)

    def test_economy_choice_changes_energy_only(self):
        upgraded = curve().upgraded("threshold", "economy", 0.5)
        self.assertEqual(upgraded.threshold.energy, 7.5)
        self.assertEqual(upgraded.threshold.speed, 12)

    def test_invalid_ordering_is_rejected(self):
        with self.assertRaises(ValueError):
            curve().upgraded("threshold", "economy", 2.1)
        with self.assertRaises(ValueError):
            curve().upgraded("threshold", "speed", 2.1)

    def test_available_choices_filter_order_breaking_upgrades(self):
        choices = curve().available_choices(
            "threshold", speed_gain=2.1, energy_reduction=2.1
        )
        self.assertEqual(choices, ())


class PhysiologyMilestoneTests(unittest.TestCase):
    def setUp(self):
        self.state = PlayerState(race_curve=curve())

    def test_milestone_has_no_automatic_effect_without_player_choice(self):
        milestone = PhysiologyMilestone("ef-1", "ef", 1, 0.5, 0.25)
        self.state.progression_ef = 3
        upgrades = apply_physiology_milestones(self.state, (milestone,), None)
        self.assertEqual(upgrades, ())
        self.assertEqual(self.state.race_curve, curve())
        self.assertEqual(self.state.progression_ef, 3)
        self.assertEqual(self.state.physiology_milestones_claimed, set())

    def test_choice_consumes_threshold_and_carries_surplus_xp(self):
        milestone = PhysiologyMilestone("ef-1", "ef", 2, 0.5, 0.25)
        self.state.progression_ef = 5
        upgrades = apply_physiology_milestones(
            self.state, (milestone,), lambda milestone, choices: "speed"
        )
        self.assertEqual(len(upgrades), 1)
        self.assertEqual(self.state.race_curve.ef.speed, 10.5)
        self.assertEqual(self.state.race_curve.ef.energy, 6)
        self.assertEqual(self.state.progression_ef, 3)
        self.assertIn("ef-1", self.state.physiology_milestones_claimed)

    def test_economy_choice_decreases_energy_without_changing_speed(self):
        milestone = PhysiologyMilestone("threshold-1", "threshold", 1, 0.5, 0.25)
        self.state.progression_threshold = 1
        apply_physiology_milestones(
            self.state, (milestone,), lambda milestone, choices: "economy"
        )
        self.assertEqual(self.state.race_curve.threshold.energy, 7.75)
        self.assertEqual(self.state.race_curve.threshold.speed, 12)

    def test_invalid_choice_is_rejected(self):
        milestone = PhysiologyMilestone("vma-1", "vma", 1, 0.5, 0.25)
        self.state.progression_vma = 1
        with self.assertRaises(ValueError):
            apply_physiology_milestones(
                self.state, (milestone,), lambda milestone, choices: "automatic"
            )

    def test_milestone_thresholds_must_increase_per_track(self):
        milestones = (
            PhysiologyMilestone("ef-2", "ef", 4, 0.5, 0.25),
            PhysiologyMilestone("ef-1", "ef", 2, 0.5, 0.25),
        )
        with self.assertRaises(ValueError):
            apply_physiology_milestones(
                self.state, milestones, lambda milestone, choices: "speed"
            )

    def test_successful_session_xp_can_trigger_player_choice(self):
        milestone = PhysiologyMilestone("ef-1", "ef", 1, 0.5, 0.25)
        budget = TrainingEnergyBudget(1, 1, 0, 0)
        result = resolve_session_plan(
            self.state, budget, ("EF1",), rpe_authorized=1,
            physiology_milestones=(milestone,),
            choose_physiology_upgrade=lambda milestone, choices: "speed",
        )
        self.assertEqual(result.xp_added, (("ef", 1), ("threshold", 0), ("vma", 0)))
        self.assertEqual(len(result.physiology_upgrades), 1)
        self.assertEqual(self.state.race_curve.ef.speed, 10.5)


if __name__ == "__main__":
    unittest.main()
