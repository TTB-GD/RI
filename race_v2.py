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
    if not is_production_physiologically_legal(profile, production, difficulty):
        raise ValueError("production and difficulty produce a load above vma")
    return RaceSegmentResult(
        production=production,
        difficulty=difficulty,
        load=load,
        score=production,
        cost=physiological_cost(profile, load),
    )


def is_production_physiologically_legal(
    profile: PhysiologyProfile, production: int, difficulty: int
) -> bool:
    """Return whether non-negative Production and Difficulty yield Charge <= VMA."""

    return production >= 0 and difficulty >= 0 and production + difficulty <= profile.vma
