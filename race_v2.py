"""Minimal integrated Race V2 rule boundary.

Race orchestration, reserve construction, player policies and Training-to-Race
conversion remain outside this module.  In particular, SPEC has no active path
here.
"""

from dataclasses import dataclass

from physiology import PhysiologyProfile, physiological_cost


@dataclass(frozen=True)
class RaceSegmentResult:
    production: int
    difficulty: int
    load: int
    score: int
    cost: int


def resolve_segment(
    profile: PhysiologyProfile, production: int, difficulty: int
) -> RaceSegmentResult:
    """Resolve Production and local Difficulty without persistent terrain state."""

    if production < 0:
        raise ValueError("production must be non-negative")
    if difficulty < 0:
        raise ValueError("difficulty must be non-negative")
    load = production + difficulty
    return RaceSegmentResult(
        production=production,
        difficulty=difficulty,
        load=load,
        score=production,
        cost=physiological_cost(profile, load),
    )
