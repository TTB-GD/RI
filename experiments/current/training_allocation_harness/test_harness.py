"""Tests for the isolated D/P/H Training allocation harness."""
from experiments.current.training_allocation_harness.harness import (
    _budget_splits, _catalogue_programs, _direct_programs, _evaluate_roll,
    retained_dice, run_experiment,
)


def test_retained_dice_uses_highest_three_without_d99():
    assert retained_dice((1, 2, 3, 4)) == (4, 3, 2)


def test_budget_splits_keep_compartments_distinct():
    splits = _budget_splits((4, 3, 2))
    assert (9, 0) in splits
    assert (0, 9) in splits
    assert (6, 3) in splits


def test_h_funds_sessions_from_matching_compartment():
    programmes = set(_catalogue_programs(4, 5))
    assert (2, 0, 1, 4, 5) in programmes
    assert (0, 1, 1, 0, 9) not in programmes
    assert (2, 1, 1, 4, 9) not in programmes


def test_direct_model_requires_each_die_to_fund_one_session():
    programmes = _direct_programs((4, 3, 2))
    assert all(sum(energy for _, energy in p) == 9 for p in programmes)


def test_ef_greater_than_quality_is_not_a_hard_constraint():
    row = _evaluate_roll((6, 6, 6, 6))
    assert row["H"]["programme_count"] > 0
    assert (0, 18) in _budget_splits(row["retained"])


def test_progression_is_reported_as_track_tokens_not_profile_gain():
    row = _evaluate_roll((6, 6, 6, 6))
    assert row["H"]["example_programmes"]
    assert all("progression_tokens" in p for p in row["H"]["example_programmes"])
    assert "profile_after" not in row["H"]["example_programmes"][0]


def test_exhaustive_harness_is_reproducible_and_scoped():
    first = run_experiment()
    second = run_experiment()
    assert first == second
    assert first["rolls"] == 6 ** 4
    assert first["d99"] == "OFF — retain highest three dice"
    assert any("EF > Quality is measured" in item for item in first["limitations"])
