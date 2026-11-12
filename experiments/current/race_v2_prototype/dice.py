"""Race V2 dice rolling, rerolls and free subset selection.

This module is deliberately independent from RaceState orchestration. It
consumes the Training dice-pool representation (face counts) and an explicit
affûtage level supplied by the Training/profile layer.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Sequence


SUPPORTED_DICE = (6, 8, 10, 12)
REROLL_CAPITAL_5K = {6: 1, 8: 2, 10: 3, 12: 4}


@dataclass(frozen=True)
class DiceDecisionResult:
    initial_faces: tuple[int, ...]
    final_faces: tuple[int, ...]
    rerolled_indices: tuple[int, ...]
    selected_indices: tuple[int, ...]
    energy_spent: int
    rerolls_used: int
    rerolls_remaining: int


def validate_dice_pool(dice_sizes: Sequence[int]) -> tuple[int, ...]:
    sizes = tuple(dice_sizes)
    if not sizes:
        raise ValueError("dice pool cannot be empty")
    if any(type(size) is not int or size not in SUPPORTED_DICE for size in sizes):
        raise ValueError("dice sizes must be integers in (6, 8, 10, 12)")
    return sizes


def reroll_capital(*, dice_sizes: Sequence[int], sector_count: int, affutage_level: int) -> int:
    """Return the global race reroll budget.

    affutage_level is the Training-derived tier: 0, 1, 2, 3 or 4, mapping
    respectively to P_affûtage = 0, .25, .50, .75 or 1.
    """
    sizes = validate_dice_pool(dice_sizes)
    if type(sector_count) is not int or sector_count not in (7, 10, 13, 16):
        raise ValueError("sector_count must be one of 7, 10, 13 or 16")
    if type(affutage_level) is not int or affutage_level not in range(5):
        raise ValueError("affutage_level must be an integer from 0 to 4")
    base = REROLL_CAPITAL_5K[max(sizes)]
    return math.ceil(base * (sector_count / 7) * (affutage_level / 4))


def roll_dice_pool(dice_sizes: Sequence[int], rng: random.Random) -> tuple[int, ...]:
    """Roll every die in the pool once, returning raw faces in pool order."""
    sizes = validate_dice_pool(dice_sizes)
    if not hasattr(rng, "randint"):
        raise TypeError("rng must expose randint")
    return tuple(rng.randint(1, size) for size in sizes)


def resolve_dice_decision(
    *,
    dice_sizes: Sequence[int],
    initial_faces: Sequence[int],
    reroll_indices: Sequence[int],
    selected_indices: Sequence[int],
    rerolls_remaining: int,
    rng: random.Random,
) -> DiceDecisionResult:
    """Apply individual rerolls, then spend any unique subset of the pool.

    A die index may occur more than once in reroll_indices: every occurrence
    is a separate reroll and replaces the preceding face. Selection occurs
    only after all rerolls and cannot contain duplicate indices.
    """
    sizes = validate_dice_pool(dice_sizes)
    faces = list(initial_faces)
    if len(faces) != len(sizes):
        raise ValueError("initial_faces length must match dice pool")
    if any(type(face) is not int or not 1 <= face <= size for face, size in zip(faces, sizes)):
        raise ValueError("each initial face must be within its die range")
    if type(rerolls_remaining) is not int or rerolls_remaining < 0:
        raise ValueError("rerolls_remaining must be a non-negative integer")
    if not hasattr(rng, "randint"):
        raise TypeError("rng must expose randint")

    rerolls = tuple(reroll_indices)
    if len(rerolls) > rerolls_remaining:
        raise ValueError("reroll decision exceeds remaining global capital")
    for index in rerolls:
        if type(index) is not int or not 0 <= index < len(sizes):
            raise ValueError("reroll index outside dice pool")
        faces[index] = rng.randint(1, sizes[index])

    selected = tuple(selected_indices)
    if len(set(selected)) != len(selected):
        raise ValueError("selected dice indices must be unique")
    if any(type(index) is not int or not 0 <= index < len(sizes) for index in selected):
        raise ValueError("selected index outside dice pool")

    return DiceDecisionResult(
        initial_faces=tuple(initial_faces),
        final_faces=tuple(faces),
        rerolled_indices=rerolls,
        selected_indices=selected,
        energy_spent=sum(faces[index] for index in selected),
        rerolls_used=len(rerolls),
        rerolls_remaining=rerolls_remaining - len(rerolls),
    )
