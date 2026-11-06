"""Unit tests for the independent CURRENT Training plan validator."""

import unittest

from plan_validation import validate_plan


class PlanValidationTests(unittest.TestCase):
    accessible = ["EF1", "EF2", "EF3", "EF4", "EF5", "Seuil3", "Seuil5", "SL5", "SL6"]

    @staticmethod
    def codes(result):
        return {violation.code for violation in result.violations}

    def test_accepts_legal_plan_and_repeatable_ef(self):
        result = validate_plan(
            ["EF2", "EF1", "Seuil3"], self.accessible,
            energy_budget=6, rpe_max=3, quality_limit=1,
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.violations, ())

    def test_accepts_risky_quality_when_bust_is_not_certain(self):
        result = validate_plan(
            ["EF2", "Seuil5"], self.accessible,
            energy_budget=7, rpe_max=4, quality_limit=1, best_die_size=6,
        )
        self.assertTrue(result.valid)

    def test_risky_quality_without_die_size_returns_structured_violation(self):
        result = validate_plan(
            ["EF2", "Seuil5"], self.accessible,
            energy_budget=7, rpe_max=4, quality_limit=1,
        )
        self.assertIn("risky_quality_missing_die_size", self.codes(result))

    def test_rejects_quality_when_bust_is_certain(self):
        result = validate_plan(
            ["EF1", "Seuil5"], self.accessible,
            energy_budget=6, rpe_max=0, quality_limit=1, best_die_size=4,
        )
        self.assertIn("risky_quality_certain_bust", self.codes(result))

    def test_collects_independent_rule_violations(self):
        result = validate_plan(
            ["EF5", "Seuil3", "Seuil3", "SL5", "SL6"], self.accessible,
            energy_budget=10, rpe_max=4, quality_limit=1, best_die_size=6,
        )
        self.assertFalse(result.valid)
        self.assertTrue({
            "duplicate_quality", "single_category_limit", "quality_limit",
            "energy_budget", "ef_above_rpe_max",
        } <= self.codes(result))

    def test_rejects_inaccessible_and_unknown_sessions(self):
        result = validate_plan(
            ["EF2", "Ghost"], ["EF1"],
            energy_budget=10, rpe_max=3, quality_limit=0,
        )
        self.assertTrue({"unknown_session", "session_not_accessible"} <= self.codes(result))

    def test_rejects_quality_without_same_turn_ef(self):
        result = validate_plan(
            ["Seuil3"], self.accessible,
            energy_budget=10, rpe_max=3, quality_limit=1,
        )
        self.assertIn("quality_requires_ef", self.codes(result))

    def test_rejects_more_than_seven_sessions(self):
        result = validate_plan(
            ["EF1"] * 8, self.accessible,
            energy_budget=8, rpe_max=1, quality_limit=0,
        )
        self.assertIn("session_limit", self.codes(result))

    def test_invalid_context_is_returned_as_structured_violation(self):
        result = validate_plan([], self.accessible, -1, 3, 0)
        self.assertFalse(result.valid)
        self.assertIn("invalid_energy_budget", self.codes(result))


if __name__ == "__main__":
    unittest.main()
