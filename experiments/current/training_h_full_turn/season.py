"""EXPERIMENTAL Training H multi-turn state and progression.

All thresholds and milestone rewards are injected fixtures. This module does
not establish GDD CURRENT rules or alter the legacy production engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .harness import DiceResolution, ProgramResolution


@dataclass(frozen=True)
class Milestone:
    key: str
    track: str
    threshold: int
    profile_gain: tuple[tuple[str, int], ...] = ()
    unlock_options: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.key or not self.track or self.threshold <= 0:
            raise ValueError("milestone needs a key, track and positive threshold")
        if any(not dimension or value <= 0
               for dimension, value in self.profile_gain):
            raise ValueError("profile gains need dimensions and positive values")


@dataclass(frozen=True)
class TrainingRules:
    fatigue_limit_by_pool_size: tuple[tuple[int, int], ...]
    milestones: tuple[Milestone, ...]
    fatigue_floor: int = 0

    def __post_init__(self):
        sizes = [size for size, _ in self.fatigue_limit_by_pool_size]
        if len(sizes) != len(set(sizes)) or any(size < 2 for size in sizes):
            raise ValueError("fatigue limits need unique pool sizes >= 2")
        if any(limit < 0 for _, limit in self.fatigue_limit_by_pool_size):
            raise ValueError("fatigue limits cannot be negative")
        if self.fatigue_floor < 0:
            raise ValueError("fatigue floor cannot be negative")
        keys = [milestone.key for milestone in self.milestones]
        if len(keys) != len(set(keys)):
            raise ValueError("milestone keys must be unique")

    def fatigue_limit(self, pool_size: int) -> int:
        limits = dict(self.fatigue_limit_by_pool_size)
        if pool_size not in limits:
            raise ValueError(f"no fatigue limit configured for {pool_size} dice")
        return limits[pool_size]


@dataclass(frozen=True)
class TrainingState:
    pool_sizes: tuple[int, ...]
    fatigue: int = 0
    turns_completed: int = 0
    progression: tuple[tuple[str, int], ...] = ()
    profile: tuple[tuple[str, int], ...] = ()
    eligible_options: tuple[str, ...] = ()
    acquired_options: tuple[str, ...] = ()
    reached_milestones: tuple[str, ...] = ()

    def __post_init__(self):
        if len(self.pool_sizes) < 2:
            raise ValueError("permanent pool must contain at least two dice")
        if self.fatigue < 0 or self.turns_completed < 0:
            raise ValueError("fatigue and turn count cannot be negative")
        if not set(self.acquired_options).issubset(self.eligible_options):
            raise ValueError("acquired options must be eligible")


def _as_dict(items):
    return dict(items)


def advance_training_turn(
    state: TrainingState,
    dice: DiceResolution,
    program: ProgramResolution,
    rules: TrainingRules,
    *,
    acquire_options: Iterable[str] = (),
) -> tuple[TrainingState, dict]:
    """Advance one turn; all player choices and risk outcomes are supplied."""
    limit = rules.fatigue_limit(len(state.pool_sizes))
    overtraining_at_start = state.fatigue > limit
    if overtraining_at_start and dice.action in {"add", "add+reroll"}:
        raise ValueError("reserve cannot be added while overtraining")

    acquired_now = tuple(acquire_options)
    if len(acquired_now) != len(set(acquired_now)):
        raise ValueError("duplicate acquisition request")

    # Every planned option (completed, failed or cancelled) must already be
    # in the portfolio at the start of this turn. A new acquisition is usable
    # only from a subsequent turn.
    attempted = list(program.completed)
    if program.failed is not None:
        attempted.append(program.failed)
    attempted.extend(program.cancelled)
    for session in attempted:
        if session.name not in state.acquired_options:
            raise ValueError(f"session option is not acquired: {session.name}")

    progression = _as_dict(state.progression)
    profile = _as_dict(state.profile)
    for session in program.completed:
        for track, points in session.adaptations:
            progression[track] = progression.get(track, 0) + points
        progression["GLOBAL"] = (
            progression.get("GLOBAL", 0) + session.global_progress
        )

    reached = set(state.reached_milestones)
    eligible = set(state.eligible_options)
    newly_reached = []
    for milestone in rules.milestones:
        if milestone.key in reached:
            continue
        if progression.get(milestone.track, 0) >= milestone.threshold:
            reached.add(milestone.key)
            newly_reached.append(milestone.key)
            for dimension, gain in milestone.profile_gain:
                profile[dimension] = profile.get(dimension, 0) + gain
            eligible.update(milestone.unlock_options)

    # Acquisition is a separate, explicit player choice after milestone
    # resolution. Newly acquired options become usable on the next turn.
    if not set(acquired_now).issubset(eligible):
        raise ValueError("cannot acquire an option that is not yet eligible")
    acquired = set(state.acquired_options)
    acquired.update(acquired_now)

    fatigue_before_floor = (
        state.fatigue
        + dice.blackjack_fatigue
        + program.imbalance_fatigue
        + program.intrinsic_fatigue
    )
    fatigue_after = max(rules.fatigue_floor, fatigue_before_floor)
    next_overtraining = fatigue_after > limit

    next_state = TrainingState(
        pool_sizes=state.pool_sizes,
        fatigue=fatigue_after,
        turns_completed=state.turns_completed + 1,
        progression=tuple(sorted(progression.items())),
        profile=tuple(sorted(profile.items())),
        eligible_options=tuple(sorted(eligible)),
        acquired_options=tuple(sorted(acquired)),
        reached_milestones=tuple(sorted(reached)),
    )
    report = {
        "turn": next_state.turns_completed,
        "fatigue_start": state.fatigue,
        "fatigue_blackjack": dice.blackjack_fatigue,
        "fatigue_imbalance": program.imbalance_fatigue,
        "fatigue_intrinsic": program.intrinsic_fatigue,
        "fatigue_before_floor": fatigue_before_floor,
        "fatigue_end": fatigue_after,
        "fatigue_limit": limit,
        "overtraining_at_start": overtraining_at_start,
        "overtraining_next_turn": next_overtraining,
        "completed_sessions": tuple(s.name for s in program.completed),
        "newly_reached_milestones": tuple(newly_reached),
        "acquired_now": acquired_now,
    }
    return next_state, report


def run_trajectory(
    initial_state: TrainingState,
    turns: Iterable[tuple[DiceResolution, ProgramResolution, tuple[str, ...]]],
    rules: TrainingRules,
) -> tuple[TrainingState, tuple[dict, ...]]:
    """Replay a deterministic sequence of player decisions and turn outcomes."""
    state = initial_state
    reports = []
    for dice, program, acquisitions in turns:
        state, report = advance_training_turn(
            state, dice, program, rules, acquire_options=acquisitions
        )
        reports.append(report)
    return state, tuple(reports)
