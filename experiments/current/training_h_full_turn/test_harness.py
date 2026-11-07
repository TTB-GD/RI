import pytest

from experiments.current.training_h_full_turn.harness import (
    Session, blackjack_fatigue, resolve_dice_action, resolve_program,
    resolve_turn,
)


def test_tn_includes_reserve_even_when_not_added():
    result = resolve_dice_action((6, 6, 6, 6), (2, 3, 4), 6, "keep")
    assert result.tn == 14
    assert result.energy == 9


def test_all_four_player_actions_are_explicit_and_deterministic():
    pool = (6, 6, 6, 6)
    assert resolve_dice_action(pool, (2, 3, 4), 5, "keep").final_dice == (2, 3, 4)
    assert resolve_dice_action(pool, (2, 3, 4), 5, "add").final_dice == (2, 3, 4, 5)
    assert resolve_dice_action(pool, (2, 3, 4), 5, "reroll", 1, 6).final_dice == (2, 6, 4)
    assert resolve_dice_action(pool, (2, 3, 4), 5, "add+reroll", 1, 6).final_dice == (2, 6, 4, 5)


def test_overtraining_disables_reserve_actions():
    with pytest.raises(ValueError):
        resolve_dice_action((6, 6, 6, 6), (2, 3, 4), 5, "add", overtraining=True)


def test_budget_split_cannot_exceed_final_energy():
    with pytest.raises(ValueError):
        resolve_program(ef_budget=5, quality_budget=5, planned_sessions=(),
                        total_energy=9)


def test_blackjack_fatigue_is_calculated_before_and_survives_bust():
    dice = resolve_dice_action((6, 6, 6, 6), (6, 6, 6), 1, "keep")
    sessions = (
        Session("EF2", "EF", 2),
        Session("VMA3", "QUALITY", 3, intrinsic_fatigue=2, risky=True),
        Session("Seuil3", "QUALITY", 3, intrinsic_fatigue=1, risky=True),
    )
    program = resolve_program(ef_budget=2, quality_budget=6,
                              planned_sessions=sessions, bust_index=1,
                              total_energy=dice.energy)
    result = resolve_turn(dice, program, prior_fatigue=4)
    assert result["fatigue_blackjack"] == blackjack_fatigue(18, 14)
    assert result["fatigue_cumulative"] >= 4 + result["fatigue_blackjack"]
    assert result["failed_session"] == "VMA3"
    assert result["cancelled_sessions"] == ("Seuil3",)
    assert result["completed_sessions"] == ("EF2",)
    assert result["fatigue_intrinsic"] == 0


def test_completed_sessions_alone_drive_tokens_and_intrinsic_fatigue():
    sessions = (
        Session("EF2", "EF", 2),
        Session("VMA3", "QUALITY", 3, intrinsic_fatigue=2, risky=True),
    )
    result = resolve_program(2, 3, sessions, bust_index=1, total_energy=5)
    assert result.progression_tokens == ("EF2",)
    assert result.intrinsic_fatigue == 0


def test_failed_session_is_not_rolled_back_into_fatigue_or_progression():
    sessions = (
        Session("EF2", "EF", 2, intrinsic_fatigue=1),
        Session("VMA3", "QUALITY", 3, intrinsic_fatigue=5, risky=True),
    )
    result = resolve_program(2, 3, sessions, bust_index=1, total_energy=5)
    assert result.intrinsic_fatigue == 1
    assert result.progression_tokens == ("EF2",)


def test_imbalance_uses_completed_sessions_not_planned_budget():
    sessions = (
        Session("EF2", "EF", 2),
        Session("VMA3", "QUALITY", 3, risky=True),
    )
    result = resolve_program(2, 3, sessions, bust_index=1, total_energy=5)
    assert result.ef_spent == 2
    assert result.quality_spent == 0
    assert result.imbalance_fatigue == 0


def test_bust_does_not_undo_prior_successful_session():
    sessions = (
        Session("EF2", "EF", 2, intrinsic_fatigue=1),
        Session("VMA3", "QUALITY", 3, risky=True),
        Session("EF1", "EF", 1, intrinsic_fatigue=1),
    )
    result = resolve_program(3, 3, sessions, bust_index=1, total_energy=6)
    assert result.progression_tokens == ("EF2", "EF1")
    assert result.intrinsic_fatigue == 2
