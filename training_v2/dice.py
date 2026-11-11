"""Explicit initial roll and Keep/Add/Reroll decisions for Training B."""
from __future__ import annotations

from dataclasses import dataclass
import random

from decision_engine import energy_and_fatigue
from dice_types import make_pool, pool_tn


def reserve_index(pool_sizes):
    """The reserve is the smallest die; ties resolve to the last pool index."""
    return min(range(len(pool_sizes)), key=lambda i: (pool_sizes[i], -i))


@dataclass(frozen=True)
class RollResult:
    """Initial roll: N-1 active dice and one unrolled reserve die.

    raw_faces is indexed like the persistent pool; the reserve slot is None
    until Add is selected. The first three positional fields retain the
    historical synthetic constructor used by tests and fixtures.
    """
    raw_faces: tuple[int | None, ...]
    final_values: tuple[int, ...]
    tn: float
    active_sizes: tuple[int, ...] = ()
    reserve_index: int = -1
    reserve_value: int | None = None
    reserve_size: int = 0

    @property
    def active_values(self):
        return self.final_values


@dataclass(frozen=True)
class DiceActionResult:
    action: str
    raw_faces: tuple[int | None, ...]
    final_values: tuple[int, ...]
    tn: float
    energy: int
    blackjack_fatigue: int
    reroll_index: int | None = None


def roll_initial(pool_sizes, *, rng=None, defer_reserve=True) -> RollResult:
    """Roll N-1 dice. The reserve is rolled only if Add is later selected."""
    rng = rng if rng is not None else random.Random()
    sizes = tuple(pool_sizes)
    if len(sizes) < 2:
        raise ValueError("dice pool must contain at least two dice")
    index = reserve_index(sizes)
    raw = [None] * len(sizes)
    active_sizes = tuple(size for i, size in enumerate(sizes) if i != index)
    active_indices = tuple(i for i in range(len(sizes)) if i != index)
    for pool_index in active_indices:
        raw[pool_index] = rng.randint(1, sizes[pool_index])
    reserve_value = None
    if not defer_reserve:
        reserve_value = rng.randint(1, sizes[index])
        raw[index] = reserve_value
    active_values = tuple(raw[i] for i in active_indices)
    return RollResult(
        raw_faces=tuple(raw), final_values=active_values, active_sizes=active_sizes,
        reserve_index=index, reserve_value=reserve_value, reserve_size=sizes[index],
        tn=pool_tn(make_pool(sizes)),
    )


def resolve_dice_action(
    roll: RollResult,
    action: str,
    *,
    reroll_index: int | None = None,
    rerolled_value: int | None = None,
    rng=None,
    overtraining: bool = False,
) -> DiceActionResult:
    """Resolve Keep, Add, Reroll or Add+Reroll after the initial roll."""
    if action not in {"keep", "add", "reroll", "add+reroll"}:
        raise ValueError("unknown dice action")
    if overtraining and action in {"add", "add+reroll"}:
        raise ValueError("reserve actions are unavailable during overtraining")

    values = list(roll.active_values)
    raw_faces = list(roll.raw_faces)
    if action in {"reroll", "add+reroll"}:
        if reroll_index is None or not 0 <= reroll_index < len(values):
            raise ValueError("reroll action requires a valid active die index")
        if rerolled_value is None:
            roller = rng if rng is not None else random.Random()
            rerolled_value = roller.randint(1, roll.active_sizes[reroll_index])
        if not 1 <= rerolled_value <= roll.active_sizes[reroll_index]:
            raise ValueError("rerolled value outside its die range")
        values[reroll_index] = rerolled_value
        active_pool_indices = [i for i in range(len(raw_faces)) if i != roll.reserve_index]
        raw_faces[active_pool_indices[reroll_index]] = rerolled_value
    elif reroll_index is not None or rerolled_value is not None:
        raise ValueError("reroll data supplied for an action without reroll")

    if action in {"add", "add+reroll"}:
        reserve_value = roll.reserve_value
        if reserve_value is None:
            roller = rng if rng is not None else random.Random()
            reserve_value = roller.randint(1, roll.reserve_size)
        if not 1 <= reserve_value <= roll.reserve_size:
            raise ValueError("reserve value outside its die range")
        raw_faces[roll.reserve_index] = reserve_value
        values.append(reserve_value)

    energy = sum(values)
    _, blackjack = energy_and_fatigue(energy, roll.tn)
    return DiceActionResult(
        action=action, raw_faces=tuple(raw_faces), final_values=tuple(values),
        tn=roll.tn, energy=energy, blackjack_fatigue=blackjack,
        reroll_index=reroll_index,
    )
