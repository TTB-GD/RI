"""Race V2 segment turn using the canonical Training B dice actions.

This is a narrow integration layer: it consumes a Training dice pool and a
caller-supplied Race reserve, then delegates segment conversion to the
physiology grid. It deliberately does not calculate reserve from CTL.
"""
from __future__ import annotations

from dataclasses import dataclass
import random

from training_v2.dice import DiceActionResult, RollResult, roll_initial, resolve_dice_action

from .physiology_grid import PhysiologyGrid, RaceSegmentResult, resolve_race_segment


@dataclass(frozen=True)
class RaceTurnResult:
    initial_roll: RollResult
    dice: DiceActionResult
    segment: RaceSegmentResult


def resolve_race_turn(
    *,
    pool_sizes: tuple[int, ...] | list[int],
    grid: PhysiologyGrid,
    difficulty: int,
    reserve_remaining: int,
    action: str,
    reroll_index: int | None = None,
    rng=None,
) -> RaceTurnResult:
    """Resolve one Race segment with Training B's N-1 / Keep-Add-Reroll flow.

    The initial roll contains N-1 active dice. The smallest die (last index
    wins ties), reserved exactly as in Training B, is rolled only for Add or
    Add+Reroll. The final dice sum is clipped at VMA by the segment resolver.
    """
    roller = rng if rng is not None else random.Random()
    initial = roll_initial(pool_sizes, rng=roller, defer_reserve=True)
    dice = resolve_dice_action(
        initial,
        action,
        reroll_index=reroll_index,
        rng=roller,
    )
    segment = resolve_race_segment(
        grid=grid,
        energy_result=dice.energy,
        difficulty=difficulty,
        reserve_remaining=reserve_remaining,
    )
    return RaceTurnResult(initial_roll=initial, dice=dice, segment=segment)
