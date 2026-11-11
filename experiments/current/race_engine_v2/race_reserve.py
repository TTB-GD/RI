"""Training-to-Race reserve preview; all balance parameters are explicit."""
from __future__ import annotations
from dataclasses import dataclass
import math
from training_v2.state import PlayerState

RACE_SEGMENT_COUNTS = {
    "5 km": 7,
    "10 km": 10,
    "half-marathon": 13,
    "marathon": 16,
}

@dataclass(frozen=True)
class FreshnessRule:
    """Convert low residual fatigue into a bounded reserve bonus."""
    fatigue_threshold: int
    bonus_per_fatigue_point: float
    max_bonus: int
    minimum_preparation_ratio: float = 0.75
    def __post_init__(self):
        if self.fatigue_threshold < 0 or self.max_bonus < 0:
            raise ValueError("freshness threshold and cap must be non-negative")
        if self.bonus_per_fatigue_point < 0:
            raise ValueError("freshness rate must be non-negative")
        if not 0 <= self.minimum_preparation_ratio <= 1:
            raise ValueError("minimum preparation ratio must be between zero and one")

@dataclass(frozen=True)
class RaceReserveProfile:
    """Course-specific total Training energy targets, independent of physiology."""
    name: str
    segments: int
    target_ef: int
    target_threshold: int
    target_vma: int
    reserve_scale: float = 1.0
    freshness: FreshnessRule = FreshnessRule(0, 0.0, 0)
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("race profile name cannot be empty")
        if self.segments < 1:
            raise ValueError("race profile must have at least one segment")
        targets = (self.target_ef, self.target_threshold, self.target_vma)
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in targets):
            raise ValueError("course targets must be non-negative integers")
        if sum(targets) <= 0:
            raise ValueError("at least one course target must be positive")
        if self.reserve_scale < 0:
            raise ValueError("reserve scale must be non-negative")

@dataclass(frozen=True)
class RaceReserveBreakdown:
    race_name: str
    segments: int
    training_turns: int
    invested_ef: int
    invested_threshold: int
    invested_vma: int
    credited_ef: int
    credited_threshold: int
    credited_vma: int
    saturated_ef: int
    saturated_threshold: int
    saturated_vma: int
    preparation_ratio: float
    preparation_reserve: int
    freshness_bonus: int
    fatigue_at_start: int
    total_reserve: int

def _round_half_up(value: float) -> int:
    return math.floor(value + 0.5)

def preview_race_reserve(state: PlayerState, profile: RaceReserveProfile) -> RaceReserveBreakdown:
    """Calculate an auditable pre-race reserve without random resolution.

    Per-track contribution is capped at the selected course objective. The
    credited total is normalized by Training turns and scaled by Race segments.
    Freshness is a capped bonus, gated by minimum preparation completion.
    """
    if not isinstance(state, PlayerState):
        raise TypeError("state must be a PlayerState")
    if not isinstance(profile, RaceReserveProfile):
        raise TypeError("profile must be a RaceReserveProfile")
    invested = (state.training_energy_ef, state.training_energy_threshold, state.training_energy_vma)
    targets = (profile.target_ef, profile.target_threshold, profile.target_vma)
    credited = tuple(min(value, target) for value, target in zip(invested, targets))
    saturated = tuple(value - credit for value, credit in zip(invested, credited))
    preparation_ratio = sum(credited) / sum(targets)
    preparation_reserve = (
        _round_half_up((sum(credited) / state.turns_played) * profile.segments * profile.reserve_scale)
        if state.turns_played else 0
    )
    rule = profile.freshness
    if preparation_ratio >= rule.minimum_preparation_ratio:
        fresh_points = max(0, rule.fatigue_threshold - state.fatigue)
        freshness_bonus = min(rule.max_bonus, _round_half_up(fresh_points * rule.bonus_per_fatigue_point))
    else:
        freshness_bonus = 0
    return RaceReserveBreakdown(
        race_name=profile.name, segments=profile.segments, training_turns=state.turns_played,
        invested_ef=invested[0], invested_threshold=invested[1], invested_vma=invested[2],
        credited_ef=credited[0], credited_threshold=credited[1], credited_vma=credited[2],
        saturated_ef=saturated[0], saturated_threshold=saturated[1], saturated_vma=saturated[2],
        preparation_ratio=preparation_ratio, preparation_reserve=preparation_reserve,
        freshness_bonus=freshness_bonus, fatigue_at_start=state.fatigue,
        total_reserve=preparation_reserve + freshness_bonus,
    )
