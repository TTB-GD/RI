"""Enumerate direct dice-to-session allocations for Training B."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

from .catalog import SESSION_CATALOG, projected_profile
from .state import PlayerState


@dataclass(frozen=True)
class SessionAllocation:
    session_key: str
    die_indices: tuple[int, ...]
    energy: int


@dataclass(frozen=True)
class ProgramOption:
    allocations: tuple[SessionAllocation, ...]
    ef_energy: int
    quality_energy: int
    session_costs: tuple[tuple[str, int], ...]
    spec_remainder: int


def _set_partitions(items):
    """Yield each set partition once; blocks are ordered by first index."""
    if not items:
        yield ()
        return
    first, *rest = items
    for partition in _set_partitions(rest):
        yield ((first,),) + partition
        for index in range(len(partition)):
            blocks = list(partition)
            blocks[index] = (first,) + blocks[index]
            yield tuple(blocks)


def list_program_options(state: PlayerState, roll: RollResult) -> tuple[ProgramOption, ...]:
    """Assign every retained die to exactly one selectable session occurrence.

    EF can repeat without a general cap. Seuil and VMA are single-occurrence
    entries in this first catalogue. No EF/Q partition or ranking is applied.
    """
    values = tuple(roll.final_values)
    if len(roll.raw_faces) != len(state.dice_pool):
        raise ValueError("roll must contain one raw face per pool die")
    if not values or len(values) > len(state.dice_pool):
        raise ValueError("roll must contain a valid retained-dice subset")
    if any(value < 1 or value > max(state.dice_pool) for value in values):
        raise ValueError("retained value is outside the pool's die range")

    options = []
    seen_signatures = set()
    keys = tuple(SESSION_CATALOG)
    for blocks in _set_partitions(tuple(range(len(values)))):
        for session_keys in product(keys, repeat=len(blocks)):
            counts = {key: session_keys.count(key) for key in keys}
            if any(
                SESSION_CATALOG[key].max_per_turn is not None
                and count > SESSION_CATALOG[key].max_per_turn
                for key, count in counts.items()
            ):
                continue

            allocations = []
            affordable = True
            for block, key in zip(blocks, session_keys):
                energy = sum(values[index] for index in block)
                if energy < SESSION_CATALOG[key].energy_cost:
                    affordable = False
                    break
                allocations.append(SessionAllocation(key, tuple(block), energy))
            if not affordable:
                continue

            projected = projected_profile(state.profile, session_keys)
            if not projected["ef"] < projected["threshold"] < projected["vma"]:
                continue

            ef_energy = sum(
                item.energy for item in allocations
                if SESSION_CATALOG[item.session_key].load_type == "EF"
            )
            quality_energy = sum(
                item.energy for item in allocations
                if SESSION_CATALOG[item.session_key].load_type == "QUALITY"
            )
            costs = tuple(
                (item.session_key, SESSION_CATALOG[item.session_key].energy_cost)
                for item in allocations
            )
            spec_remainder = sum(
                item.energy - SESSION_CATALOG[item.session_key].energy_cost
                for item in allocations
                if SESSION_CATALOG[item.session_key].load_type == "QUALITY"
            )
            signature = tuple(sorted((item.session_key, item.energy) for item in allocations))
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            allocations.sort(key=lambda item: (item.session_key, item.energy, item.die_indices))
            options.append(ProgramOption(
                allocations=tuple(allocations),
                ef_energy=ef_energy,
                quality_energy=quality_energy,
                session_costs=costs,
                spec_remainder=spec_remainder,
            ))
    return tuple(options)
