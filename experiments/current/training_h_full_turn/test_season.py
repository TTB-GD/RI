import pytest

from experiments.current.training_h_full_turn.harness import (
    Session, resolve_dice_action, resolve_program,
)
from experiments.current.training_h_full_turn.season import (
    Milestone, TrainingRules, TrainingState, advance_training_turn,
    run_trajectory,
)


@pytest.fixture
def rules():
    # Deliberately small fixture values, not balance recommendations.
    return TrainingRules(
        fatigue_limit_by_pool_size=((4, 6),),
        milestones=(
            Milestone("ef-1", "EF", 2, (("EF", 1),), ("EF_plus",)),
            Milestone("global-1", "GLOBAL", 3, (("Durability", 1),), ("SL_base",)),
        ),
    )


def turn(pool, active, reserve, action, sessions, ef, quality,
         *, bust=None, reroll_index=None, rerolled_value=None):
    dice = resolve_dice_action(
        pool, active, reserve, action, reroll_index, rerolled_value
    )
    program = resolve_program(
        ef, quality, sessions, bust_index=bust, total_energy=dice.energy
    )
    return dice, program


def test_fatigue_persists_and_reserve_is_restricted_only_next_turn(rules):
    state = TrainingState((6, 6, 6, 6), fatigue=5,
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",))
    dice, program = turn(
        (6, 6, 6, 6), (6, 6, 6), 1, "keep",
        (Session("EF_base", "EF", 2),), 2, 0
    )
    next_state, report = advance_training_turn(state, dice, program, rules)
    assert report["overtraining_at_start"] is False
    assert report["overtraining_next_turn"] is True
    assert next_state.fatigue > 6

    # The next turn cannot consume the reserve, but may reroll an active die.
    dice2 = resolve_dice_action(
        state.pool_sizes, (2, 3, 4), 5, "reroll", 0, 4,
        overtraining=report["overtraining_next_turn"]
    )
    assert dice2.action == "reroll"
    with pytest.raises(ValueError):
        resolve_dice_action(
            state.pool_sizes, (2, 3, 4), 5, "add",
            overtraining=report["overtraining_next_turn"]
        )


def test_recovery_below_limit_restores_reserve_on_following_turn(rules):
    state = TrainingState((6, 6, 6, 6), fatigue=7,
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",))
    # With TN=14, energy=6 gives a -8 offset and a recovery of 3.
    dice = resolve_dice_action((6, 6, 6, 6), (2, 2, 2), 6, "keep")
    program = resolve_program(0, 0, (), total_energy=dice.energy)
    recovered, report = advance_training_turn(state, dice, program, rules)
    assert report["overtraining_at_start"] is True
    assert recovered.fatigue == 4
    assert report["overtraining_next_turn"] is False
    # Add is legal again after recovery has completed.
    dice2 = resolve_dice_action((6, 6, 6, 6), (2, 3, 4), 5, "add",
                                overtraining=report["overtraining_next_turn"])
    assert dice2.action == "add"


def test_failed_session_does_not_contribute_to_multiturn_progression(rules):
    state = TrainingState((6, 6, 6, 6),
                          eligible_options=("EF_base", "VMA_base"),
                          acquired_options=("EF_base", "VMA_base"))
    sessions = (
        Session("EF_base", "EF", 2, adaptations=(("EF", 2),)),
        Session("VMA_base", "QUALITY", 3, adaptations=(("VMA", 3),),
                risky=True),
    )
    dice, program = turn((6, 6, 6, 6), (4, 4, 4), 4, "keep",
                         sessions, 2, 3, bust=1)
    next_state, report = advance_training_turn(state, dice, program, rules)
    assert dict(next_state.progression) == {"EF": 2, "GLOBAL": 0}
    assert dict(next_state.profile) == {"EF": 1}
    assert report["newly_reached_milestones"] == ("ef-1",)
    assert "SL_base" not in next_state.eligible_options


def test_global_milestone_unlocks_eligibility_not_automatic_acquisition(rules):
    state = TrainingState((6, 6, 6, 6),
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",))
    sessions = (
        Session("EF_base", "EF", 2, adaptations=(("EF", 1),),
                global_progress=3),
    )
    dice, program = turn((6, 6, 6, 6), (3, 3, 3), 3, "keep",
                         sessions, 2, 0)
    next_state, report = advance_training_turn(state, dice, program, rules)
    assert "SL_base" in next_state.eligible_options
    assert "SL_base" not in next_state.acquired_options
    assert report["newly_reached_milestones"] == ("global-1",)


def test_newly_unlocked_option_can_be_acquired_only_by_explicit_choice(rules):
    state = TrainingState((6, 6, 6, 6),
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",))
    sessions = (
        Session("EF_base", "EF", 2, adaptations=(("EF", 2),)),
    )
    dice, program = turn((6, 6, 6, 6), (3, 3, 3), 3, "keep",
                         sessions, 2, 0)
    next_state, _ = advance_training_turn(
        state, dice, program, rules, acquire_options=("EF_plus",)
    )
    assert "EF_plus" in next_state.acquired_options


def test_profile_milestone_is_one_shot_even_after_more_progress(rules):
    state = TrainingState((6, 6, 6, 6),
                          progression=(("EF", 2),),
                          profile=(("EF", 1),),
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",),
                          reached_milestones=("ef-1",))
    sessions = (
        Session("EF_base", "EF", 2, adaptations=(("EF", 10),)),
    )
    dice, program = turn((6, 6, 6, 6), (3, 3, 3), 3, "keep",
                         sessions, 2, 0)
    next_state, report = advance_training_turn(state, dice, program, rules)
    assert dict(next_state.profile)["EF"] == 1
    assert report["newly_reached_milestones"] == ()


def test_trajectory_replays_3_6_12_and_16_turn_sequences(rules):
    state = TrainingState((6, 6, 6, 6),
                          eligible_options=("EF_base",),
                          acquired_options=("EF_base",))
    dice = resolve_dice_action((6, 6, 6, 6), (3, 3, 3), 3, "keep")
    program = resolve_program(
        2, 0, (Session("EF_base", "EF", 2, adaptations=(("EF", 1),)),),
        total_energy=dice.energy
    )
    for count in (3, 6, 12, 16):
        final_state, reports = run_trajectory(
            state, ((dice, program, ()) for _ in range(count)), rules
        )
        assert final_state.turns_completed == count
        assert len(reports) == count
