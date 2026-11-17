import numpy as np
from simulate import energy_cost, energy_output, target_for, play_course


def test_curve_anchors_and_interpolation():
    assert [energy_cost(x) for x in range(9, 18)] == [1, 1, 2, 3, 4, 5, 7, 10, 13]


def test_caps():
    assert energy_cost(8) == 0
    assert energy_output(8) == 8
    assert energy_cost(18) == 13
    assert energy_output(18) == 17


def test_targets():
    assert target_for("opportunistic", 8, 8) == 15
    assert target_for("long_term", 8, 8) == 10
    assert target_for("long_term", 1, 7) == 10
    assert target_for("long_term", 0, 7) == 8


def test_course_metrics_are_bounded():
    result = play_course(4, "long_term", np.random.default_rng(42))
    assert 0 <= result["energy"] <= 8 * 17
    assert 0 <= result["sustainability_spent"] <= 8
    assert 0 <= result["rerolls_used"] <= 4 * 4
    assert 0 <= result["ef_locked_turns"] <= 8
