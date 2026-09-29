"""Tests for the isolated SPEC experiment, not CURRENT behavior."""

import unittest

from experiments.current.training_v2_specific.harness import (
    State, _award_spec_tiers, allocate_q, curve_comparison, enumerate_headroom,
    _award_d4_tier, run_d1, run_d4a, run_d4b, simulate, simulate_d4,
)


class SpecificHarnessTests(unittest.TestCase):
    def test_switch_tie_prefers_physiology(self):
        state = State("AS42", "S1")
        attempts, spec, unused = allocate_q(state, 5, "G_SWITCH")
        self.assertEqual(attempts, [("SEUIL", 3)])
        self.assertEqual((spec, unused), (2, 0))

    def test_speed_saturation_forces_eco(self):
        state = State("AS42", "S1", as_value=8)
        state.progression_spec = 5
        self.assertEqual(_award_spec_tiers(state, "SPEED"), ["ECO"])
        self.assertEqual((state.as_value, state.eco), (8, 1))

    def test_q_accounting_and_reproducibility(self):
        first, _ = simulate(7, "AS10", "S2", "G_SWITCH")
        second, _ = simulate(7, "AS10", "S2", "G_SWITCH")
        self.assertEqual(first, second)
        self.assertEqual(first["q_total"], first["q_phys"] + first["q_spec"] + first["q_unused"])

    def test_curve_ignores_physiology_and_c2_uses_half_up(self):
        self.assertEqual(curve_comparison(9, 3, "C2")[1]["cost"], 0)
        self.assertEqual(curve_comparison(9, 3, "C2"), curve_comparison(9, 3, "C2"))

    def test_d1_protocol_size(self):
        result, _ = run_d1(2)
        self.assertEqual(result["total_turns"], 576)
        self.assertEqual(len(result["cells"]), 18)

    def test_headroom_enumeration_reopens_exactly_one_shell(self):
        row = enumerate_headroom("AS42", 6, 8)
        self.assertEqual((row["headroom"], row["build_count"]), (2, 6))
        self.assertEqual(row["new_build_count"], 4)
        self.assertTrue(all(build["as_relative"] + build["eco"] == 3
                            for build in row["new_builds"]))

    def test_d4a_confirms_all_fixtures(self):
        result = run_d4a()
        self.assertEqual(len(result["rows"]), 8)
        self.assertTrue(result["headroom_reopens_useful_nontrivial_capacity"])

    def test_d4_is_reproducible_and_conserves_q(self):
        first, _ = simulate_d4(9, "AS10")
        second, _ = simulate_d4(9, "AS10")
        self.assertEqual(first, second)
        self.assertEqual(first["q_total"], first["q_phys"] + first["q_spec"] + first["q_unused"])

    def test_d4_saturation_blocks_tier_conversion(self):
        state = State("AS10", "S2", as_value=10)
        state.progression_spec = 5
        self.assertEqual(_award_d4_tier(state), [])
        self.assertEqual(state.spec_tiers, 0)

    def test_d4_protocol_and_observed_classification(self):
        result = run_d4b()
        self.assertEqual(result["total_turns"], 960)
        self.assertEqual(result["classification"], "ALTERNANCE RARE")
        self.assertEqual(result["cells"]["AS42"]["runs_with_alternation_pct"], 0)
        self.assertGreater(result["cells"]["AS10"]["runs_with_alternation_pct"], 50)


if __name__ == "__main__":
    unittest.main()
