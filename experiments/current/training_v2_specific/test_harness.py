"""Tests for the isolated SPEC experiment, not CURRENT behavior."""

import unittest

from experiments.current.training_v2_specific.harness import (
    State, _award_spec_tiers, allocate_q, curve_comparison, run_d1, simulate,
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


if __name__ == "__main__":
    unittest.main()
