"""CI coverage for the experimental pool-normalized cost probe."""
import json
import unittest

from experiments.current.training_race_bridge.pool_normalized_cost_probe import run_matrix


class PoolNormalizedCostProbeTests(unittest.TestCase):
    def test_nine_training_b_cases_run_with_explicit_pool_normalization(self):
        result = run_matrix()
        print("POOL_NORMALIZED_SUMMARY=" + json.dumps(result["summary"], sort_keys=True))
        self.assertEqual(len(result["courses"]), 9)
        self.assertTrue(result["protocol"]["reserve_interpretation_is_hypothesis"])
        for course in result["courses"]:
            self.assertGreater(course["pool_expected_total"], 0)
            self.assertGreaterEqual(course["race_spent"], 0)
            self.assertEqual(len(course["race_turns"]), course["race_dnf_turn"] - 1
                             if course["race_dnf"] else 6)
        for focus in ("balanced", "ef", "quality"):
            self.assertEqual(len(result["summary"][focus]["profiles"]), 3)


if __name__ == "__main__":
    unittest.main()
