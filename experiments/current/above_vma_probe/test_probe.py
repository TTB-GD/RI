import unittest

from physiology import PhysiologyProfile, physiological_cost

from experiments.current.above_vma_probe.probe import (
    OVERLOAD_COEFFICIENTS,
    PROFILES,
    build_results,
    overload,
    variant_a_legal,
    variant_b_cost,
    variant_c_cost,
)


class AboveVmaProbeTests(unittest.TestCase):
    def setUp(self):
        self.profile = PhysiologyProfile(0, 5, 10)

    def test_exact_overload_and_variant_a_legality(self):
        self.assertEqual(overload(self.profile, 10), 0)
        self.assertEqual(overload(self.profile, 11), 1)
        self.assertEqual(overload(self.profile, 13), 3)
        self.assertTrue(variant_a_legal(self.profile, 8, 2))
        self.assertFalse(variant_a_legal(self.profile, 9, 2))

    def test_variant_b_continues_post_threshold_slope(self):
        self.assertEqual(physiological_cost(self.profile, 10), 25)
        self.assertEqual([variant_b_cost(self.profile, charge) for charge in range(10, 14)],
                         [25, 28, 31, 34])

    def test_variant_c_coefficients(self):
        self.assertEqual(
            {coefficient: variant_c_cost(self.profile, 12, coefficient)
             for coefficient in OVERLOAD_COEFFICIENTS},
            {2: 29, 3: 31, 4: 33},
        )
        with self.assertRaises(ValueError):
            variant_c_cost(self.profile, 12, 5)

    def test_all_costs_are_monotone_across_the_probe_range(self):
        for name, profile in PROFILES.items():
            charges = range(profile.vma - 3, profile.vma + 4)
            with self.subTest(profile=name, variant="B"):
                costs = [variant_b_cost(profile, charge) for charge in charges]
                self.assertTrue(all(left < right for left, right in zip(costs, costs[1:])))
            for coefficient in OVERLOAD_COEFFICIENTS:
                with self.subTest(profile=name, variant=f"C{coefficient}"):
                    costs = [variant_c_cost(profile, charge, coefficient) for charge in charges]
                    self.assertTrue(all(left < right for left, right in zip(costs, costs[1:])))

    def test_variants_match_integrated_cost_at_or_below_vma(self):
        for profile in PROFILES.values():
            for charge in range(profile.vma - 3, profile.vma + 1):
                native = physiological_cost(profile, charge)
                self.assertEqual(variant_b_cost(profile, charge), native)
                for coefficient in OVERLOAD_COEFFICIENTS:
                    self.assertEqual(variant_c_cost(profile, charge, coefficient), native)

    def test_grid_is_complete_and_contains_required_cases(self):
        results = build_results()
        self.assertEqual(len(results["configurations"]), 48)
        p1 = [row for row in results["configurations"] if row["profile"] == "P1"]
        required = {(8, 2), (9, 2), (10, 1), (10, 3)}
        self.assertTrue(required <= {(row["production"], row["difficulty"]) for row in p1})


if __name__ == "__main__":
    unittest.main()
