"""Local tests for the experimental probe; these are not CURRENT tests."""

import unittest

from experiments.current.race_efficiency_probe.harness import (
    CURVES, EF, VMA, adjusted_cost, eco_max, native_cost, run_probe,
)


class RaceEfficiencyProbeTests(unittest.TestCase):
    def test_native_curves_are_strictly_monotone(self):
        for curve in CURVES:
            costs = [native_cost(curve, x) for x in range(EF, VMA + 1)]
            self.assertTrue(all(left < right for left, right in zip(costs, costs[1:])))

    def test_domain_boundaries_are_enforced(self):
        for curve in CURVES:
            native_cost(curve, EF)
            native_cost(curve, VMA)
            with self.assertRaises(ValueError):
                native_cost(curve, EF - 1)
            with self.assertRaises(ValueError):
                native_cost(curve, VMA + 1)

    def test_envelope_is_nonnegative_and_zero_at_boundaries(self):
        for curve in CURVES:
            self.assertEqual(eco_max(curve, EF), 0)
            self.assertEqual(eco_max(curve, VMA), 0)
            self.assertTrue(all(eco_max(curve, x) >= 0 for x in range(EF, VMA + 1)))

    def test_adjusted_cost_never_falls_below_EF_cost(self):
        for curve in CURVES:
            floor = native_cost(curve, EF)
            for x in range(EF, VMA + 1):
                self.assertGreaterEqual(adjusted_cost(curve, x, 1000)[0], floor)

    def test_probe_is_deterministic(self):
        self.assertEqual(run_probe(), run_probe())


if __name__ == "__main__":
    unittest.main()

