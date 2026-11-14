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

    def test_ef_speed_milestone_translates_all_three_anchors(self):
        upgraded = curve().upgraded("ef", "speed", 0.5)
        self.assertEqual(
            (upgraded.ef.speed, upgraded.threshold.speed, upgraded.vma.speed),
            (10.5, 12.5, 14.5),
        )
        self.assertEqual(
            (upgraded.ef.energy, upgraded.threshold.energy, upgraded.vma.energy),
            (6, 8, 10),
        )
        self.assertEqual(
            upgraded.threshold.speed - upgraded.ef.speed,
            curve().threshold.speed - curve().ef.speed,
        )

    def test_ef_economy_milestone_translates_all_three_energy_anchors(self):
        upgraded = curve().upgraded("ef", "economy", 0.25)
        self.assertEqual(
            (upgraded.ef.energy, upgraded.threshold.energy, upgraded.vma.energy),
            (5.75, 7.75, 9.75),
        )
        self.assertEqual(
            (upgraded.ef.speed, upgraded.threshold.speed, upgraded.vma.speed),
            (10, 12, 14),
        )

    def test_quality_milestone_changes_only_its_target_anchor(self):
        upgraded = curve().upgraded("threshold", "speed", 0.5)
        self.assertEqual(upgraded.ef, curve().ef)
        self.assertEqual(upgraded.threshold, PhysiologyPoint(8, 12.5))
        self.assertEqual(upgraded.vma, curve().vma)

    def test_quality_economy_choice_changes_only_target_energy(self):
        upgraded = curve().upgraded("threshold", "economy", 0.5)
        self.assertEqual(upgraded.ef, curve().ef)
        self.assertEqual(upgraded.threshold, PhysiologyPoint(7.5, 12))
        self.assertEqual(upgraded.vma, curve().vma)

    def test_invalid_ordering_or_non_positive_energy_is_rejected(self):
        with self.assertRaises(ValueError):
            curve().upgraded("threshold", "economy", 2.1)
        with self.assertRaises(ValueError):
            curve().upgraded("threshold", "speed", 2.1)
        with self.assertRaises(ValueError):
            curve().upgraded("ef", "economy", 6)

    def test_available_choices_filter_invalid_ef_upgrade(self):
        choices = curve().available_choices(
            "ef", speed_gain=2.1, energy_reduction=6
        )
        self.assertEqual(choices, ("speed",))


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

    def test_ef_choice_consumes_threshold_and_carries_surplus_xp(self):
        milestone = PhysiologyMilestone("ef-1", "ef", 2, 0.5, 0.25)
        self.state.progression_ef = 5
        upgrades = apply_physiology_milestones(
            self.state, (milestone,), lambda milestone, choices: "speed"
        )
        self.assertEqual(len(upgrades), 1)
        self.assertEqual(
            (self.state.race_curve.ef.speed,
             self.state.race_curve.threshold.speed,
             self.state.race_curve.vma.speed),
            (10.5, 12.5, 14.5),
        )
        self.assertEqual(self.state.progression_ef, 3)
        self.assertIn("ef-1", self.state.physiology_milestones_claimed)

    def test_quality_choice_remains_local_to_one_anchor(self):
        milestone = PhysiologyMilestone("threshold-1", "threshold", 1, 0.5, 0.25)
        self.state.progression_threshold = 1
        apply_physiology_milestones(
            self.state, (milestone,), lambda milestone, choices: "economy"
        )
        self.assertEqual(self.state.race_curve.ef, curve().ef)
        self.assertEqual(self.state.race_curve.threshold, PhysiologyPoint(7.75, 12))
        self.assertEqual(self.state.race_curve.vma, curve().vma)

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

    def test_successful_ef_session_can_trigger_cross_anchor_choice(self):
        milestone = PhysiologyMilestone("ef-1", "ef", 1, 0.5, 0.25)
        budget = TrainingEnergyBudget(1, 1, 0, 0)
        result = resolve_session_plan(
            self.state, budget, ("EF1",), rpe_authorized=1,
            physiology_milestones=(milestone,),
            choose_physiology_upgrade=lambda milestone, choices: "speed",
        )
        self.assertEqual(result.xp_added, (("ef", 1), ("threshold", 0), ("vma", 0)))
        self.assertEqual(len(result.physiology_upgrades), 1)
        self.assertEqual(
            (self.state.race_curve.ef.speed,
             self.state.race_curve.threshold.speed,
             self.state.race_curve.vma.speed),
            (10.5, 12.5, 14.5),
        )


if __name__ == "__main__":
    unittest.main()
