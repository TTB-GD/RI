import random
import unittest

from experiments.p0_selector_audit.harness import (
    audit_choose,
    legality,
    marginal_components,
    simulate_audited,
)
from overtraining_capacity_harness import simulate
from session_selector import _SelectionState, choose_sessions_weighted


class TestP0AuditInstrumentation(unittest.TestCase):
    def test_instrumented_selection_exactly_matches_production_and_does_not_touch_rng(self):
        available = ["EF1", "EF2", "Seuil3"]
        before = random.getstate()
        audited = audit_choose(0, 1, available, 10, 4, 14, -3, 6, [6, 6, 6, 6])
        after = random.getstate()
        expected, _ = choose_sessions_weighted(available, 10, 4, 14)
        self.assertEqual(audited["chosen"], expected)
        self.assertEqual(before, after)

    def test_marginal_components_sum_to_total(self):
        state = _SelectionState(chosen=["EF2"], energy_used=2, ef_this_turn=1)
        components = marginal_components("Seuil3", state, 10, 4, 14)
        component_sum = sum(components[name] for name in (
            "delta_energy_term", "delta_quality_term", "delta_rpe_term", "delta_fatigue_term"
        ))
        self.assertAlmostEqual(component_sum, components["marginal_utility"])
        self.assertAlmostEqual(
            components["utility_after"] - components["utility_before"],
            components["marginal_utility"],
        )

    def test_legality_reports_production_check_order(self):
        state = _SelectionState()
        self.assertEqual(legality("Seuil3", state, 10, 2), (False, "rpe_max"))
        self.assertEqual(legality("Seuil3", state, 10, 2, ignore_rpe=True),
                         (False, "quality_requires_ef"))
        state = _SelectionState(chosen=["EF1"], energy_used=1, ef_this_turn=1)
        self.assertEqual(legality("Seuil3", state, 3, 4), (False, "energy_budget"))

    def test_stop_reason_reproduces_actual_negative_margin_condition(self):
        audited = audit_choose(0, 1, ["EF1", "EF2", "Seuil3"], 20, 4, 14, -3, 6, [6]*4)
        if audited["stop_reason"] == "marginal_utility_negative":
            legal = [row for row in audited["stop_records"] if row["legal"]]
            self.assertLess(max(row["marginal_utility"] for row in legal), 0)
        else:
            self.assertFalse(any(row["legal"] for row in audited["stop_records"]))

    def test_audited_trajectory_matches_uninstrumented_p0(self):
        for seed in range(3):
            baseline, baseline_sessions = simulate(seed, "P0_CURRENT", turns=6)
            audited, _, _ = simulate_audited(seed, turns=6)
            for expected, actual in zip(baseline, audited):
                expected_names = [row["session"] for row in baseline_sessions
                                  if row["turn"] == expected["turn"] and row["realized"]]
                self.assertEqual(actual["sessions"].split("-") if actual["sessions"] else [], expected_names)
                self.assertEqual(actual["energy_used"], expected["spend_effective"])
                self.assertEqual(actual["ctl_after"], expected["ctl"])
                self.assertEqual(actual["quality_total_after"], expected["quality_total"])
                self.assertEqual(actual["pool_active"], expected["pool_active"])
                self.assertEqual(actual["pool_permanent_after"], expected["pool_permanent"])
                self.assertEqual(actual["q"], expected["q"])
                self.assertEqual(actual["s"], expected["s_effective"])
                self.assertEqual(actual["recovery"], expected["recovery"])


if __name__ == "__main__":
    unittest.main()
