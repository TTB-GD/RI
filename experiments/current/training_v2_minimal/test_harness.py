"""Tests for the isolated Training V2 experiment, not CURRENT behavior."""

import ast
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_experimental_json import TRAINING_RESULTS, validate_repository

from experiments.current.training_v2_minimal.harness import (
    affordable_programs, experiment_a, experiment_a2, experiment_c,
    legal_partitions, quality_cost, resolve_roll, simulate, simulate_b2,
    run_all, update_second_pass,
)


class TrainingV2HarnessTests(unittest.TestCase):
    def test_cost_boundaries(self):
        self.assertEqual(quality_cost(8, 6), 3)
        self.assertEqual(quality_cost(12, 6), 7)
        self.assertEqual(quality_cost(13, 6), 9)
        self.assertEqual(quality_cost(28, 6), 27)

    def test_example_partitions_are_physical_and_legal(self):
        rows = legal_partitions((5, 4, 3, 2))
        energies = {(ef, q) for ef, q, _ in rows}
        self.assertTrue({(9, 5), (8, 6), (7, 7)} <= energies)
        self.assertNotIn((5, 9), energies)
        self.assertTrue(all(ef >= q for ef, q, _ in rows))

    def test_d99_only_controls_reserve(self):
        self.assertEqual(resolve_roll((5, 5, 3, 3)), (5, 5, 3, 3))
        self.assertEqual(resolve_roll((6, 5, 4, 3)), (6, 5, 4))
        self.assertEqual(resolve_roll((5, 5, 3, 3), "D99_OFF"), (5, 5, 3))

    def test_exhaustive_a_is_stable(self):
        result = experiment_a()
        self.assertEqual(result["raw_outcomes"], 1296)
        self.assertEqual(result["criterion"], "CHOIX REEL")

    def test_longitudinal_is_reproducible_and_ordered(self):
        first, _ = simulate(17, "P_BALANCED")
        second, _ = simulate(17, "P_BALANCED")
        self.assertEqual(first, second)
        self.assertLess(first["EF"], first["SEUIL"])
        self.assertLess(first["SEUIL"], first["VMA"])

    def test_c_profiles_share_spec_investment(self):
        rows = experiment_c()["rows"]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["speed"] + -row["eco"] == 4 for row in rows))

    def test_a2_requires_sum_of_costs_for_double_quality(self):
        self.assertNotIn(("SEUIL", "VMA"),
                         [row["qualities"] for row in affordable_programs(7, 6, 8, 10)])
        double = next(row for row in affordable_programs(9, 6, 8, 10)
                      if row["qualities"] == ("SEUIL", "VMA"))
        self.assertEqual((double["consumed"], double["remainder"]), (8, 1))

    def test_a2_is_exhaustive_and_uses_true_simultaneous_program(self):
        result = experiment_a2()
        self.assertEqual(result["raw_outcomes"], 1296)
        self.assertLess(result["seuil_plus_vma_same_partition_pct"], result["vma_pct"])

    def test_q_spent_spec_conserves_q_energy_except_bust_loss(self):
        record, _ = simulate_b2(17, "P_QUALITY", "Q_SPENT_SPEC")
        self.assertEqual(record["q_available"], record["q_consumed"]
                         + record["q_to_spec"] + record["q_lost_bust"])
        self.assertEqual(record["progression_Q"], record["q_consumed"])

    def test_b2_is_reproducible(self):
        first, _ = simulate_b2(29, "P_BALANCED", "Q_FULL")
        second, _ = simulate_b2(29, "P_BALANCED", "Q_FULL")
        self.assertEqual(first, second)

    @patch("experiments.current.training_v2_minimal.harness.experiment_c")
    @patch("experiments.current.training_v2_minimal.harness.experiment_b2")
    @patch("experiments.current.training_v2_minimal.harness.experiment_b")
    @patch("experiments.current.training_v2_minimal.harness.experiment_a2")
    @patch("experiments.current.training_v2_minimal.harness.experiment_a")
    def test_run_all_keeps_every_block(self, a, a2, b, b2, c):
        a.return_value = {"criterion": "CHOIX REEL"}
        a2.return_value = {"probe": "A2"}
        b.return_value = {"probe": "B"}
        b2.return_value = {"probe": "B2"}
        c.return_value = {"probe": "C"}

        self.assertEqual(set(run_all()), {"status", "A", "A2", "B", "B2", "C"})

    def test_invalid_history_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "results.json"
            invalid = '{"status": "historical"'
            destination.write_text(invalid, encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "historical results.*invalid"):
                update_second_pass(destination)

            self.assertEqual(destination.read_text(encoding="utf-8"), invalid)

    def test_harness_has_one_main_entry_point(self):
        tree = ast.parse(Path(__file__).with_name("harness.py").read_text(encoding="utf-8"))
        guard = ast.dump(ast.parse('__name__ == "__main__"', mode="eval").body)
        entries = [node for node in ast.walk(tree)
                   if isinstance(node, ast.If) and ast.dump(node.test) == guard]
        self.assertEqual(len(entries), 1)
        self.assertIn(entries[0], tree.body)
        self.assertEqual(ast.dump(entries[0].body[0]), ast.dump(ast.parse("main()").body[0]))
        self.assertEqual(len(entries[0].body), 1)


class JsonEvidenceTests(unittest.TestCase):
    """Mutate temporary tracked evidence only; never regenerate experiments."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.destination = self.root / TRAINING_RESULTS
        self.destination.parent.mkdir(parents=True)
        self.original = Path(__file__).with_name("results.json").read_text(encoding="utf-8")
        self.destination.write_text(self.original, encoding="utf-8")
        self.track(TRAINING_RESULTS)

    def track(self, relative):
        subprocess.run(["git", "-C", str(self.root), "add", "--", relative], check=True)

    def write_result(self, result):
        self.destination.write_text(json.dumps(result), encoding="utf-8")

    def test_valid_tracked_json_and_untracked_outputs_ignored(self):
        (self.root / "local-output.json").write_text("{broken", encoding="utf-8")
        self.assertEqual(validate_repository(self.root), 1)
        self.assertEqual(self.destination.read_text(encoding="utf-8"), self.original)

    def test_invalid_tracked_json_rejected_without_overwrite(self):
        for relative in (TRAINING_RESULTS, "other-evidence.json"):
            with self.subTest(path=relative):
                self.destination.write_text(self.original, encoding="utf-8")
                path = self.root / relative
                path.write_text("{broken", encoding="utf-8")
                self.track(relative)
                with self.assertRaises(ValueError):
                    validate_repository(self.root)
                self.assertEqual(path.read_text(encoding="utf-8"), "{broken")

    def test_required_result_must_exist_and_be_tracked(self):
        self.destination.unlink()
        with self.assertRaisesRegex(ValueError, "results.json"):
            validate_repository(self.root)
        self.destination.write_text(self.original, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "rm", "--cached", "--quiet",
                        "--", TRAINING_RESULTS], check=True)
        with self.assertRaisesRegex(ValueError, "required tracked JSON missing"):
            validate_repository(self.root)

    def test_missing_blocks_are_rejected(self):
        for block in ("A", "A2", "B", "B2", "C"):
            with self.subTest(block=block):
                result = json.loads(self.original)
                del result[block]
                self.write_result(result)
                with self.assertRaisesRegex(ValueError, f"block {block} "):
                    validate_repository(self.root)

    def test_null_empty_and_wrong_block_types_are_rejected(self):
        for block in ("A", "A2", "B", "B2", "C"):
            for replacement in (None, {}, [], "placeholder"):
                with self.subTest(block=block, replacement=replacement):
                    result = json.loads(self.original)
                    result[block] = replacement
                    self.write_result(result)
                    with self.assertRaisesRegex(ValueError, f"block {block} "):
                        validate_repository(self.root)

    def test_essential_nested_containers_are_checked(self):
        for block, replacement in (("A", {"raw_outcomes": None}),
                                   ("A2", {"raw_outcomes": True}),
                                   ("B", {"policies": {}}),
                                   ("B2", {"cells": {"cell": None}}),
                                   ("C", {"rows": [None]})):
            with self.subTest(block=block):
                result = json.loads(self.original)
                result[block] = replacement
                self.write_result(result)
                with self.assertRaisesRegex(ValueError, f"Training V2 {block}\\."):
                    validate_repository(self.root)

    def test_duplicate_keys_and_non_json_constants_are_rejected(self):
        extra = self.root / "other-evidence.json"
        for text in ('{"B2": {}, "B2": {}}', '{"value": NaN}', '{"value": Infinity}'):
            with self.subTest(text=text):
                extra.write_text(text, encoding="utf-8")
                self.track(extra.name)
                with self.assertRaises(ValueError):
                    validate_repository(self.root)


if __name__ == "__main__":
    unittest.main()
