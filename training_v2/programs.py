"""Enumerate player-selectable Training B programmes after a roll.

The module exposes feasible choices without selecting or ranking a preferred
programme. Costs and progression thresholds remain experimental B2 values.
"""
from dataclasses import dataclass
from itertools import combinations

from .catalog import QUALITY_CATALOG, projected_profile, quality_cost
from .engine import RollResult
from .state import PlayerState


@dataclass(frozen=True)
class ProgramOption:
    ef_indices: tuple[int, ...]
    quality_indices: tuple[int, ...]
    ef_energy: int
    quality_energy: int
    qualities: tuple[str, ...]
    quality_costs: tuple[tuple[str, int], ...]
    spec_remainder: int


def list_program_options(state: PlayerState, roll: RollResult) -> tuple[ProgramOption, ...]:
    """Return every affordable physical partition/program for this roll.

    An empty quality programme is included, allowing the player to route all Q
    energy to the experimental SPEC counter. Profile legality is evaluated from
    the fixed adaptations declared by each selected catalogue entry.
    """
    values = tuple(roll.final_values)
    if len(roll.raw_faces) != len(state.dice_pool):
        raise ValueError("roll must contain one raw face per pool die")
    if not values or len(values) > len(state.dice_pool):
        raise ValueError("roll must contain a valid retained-dice subset")
    if any(value < 1 or value > max(state.dice_pool) for value in values):
        raise ValueError("retained value is outside the pool's die range")

    names = tuple(QUALITY_CATALOG)
    options = []
    indices = range(len(values))

    for quality_count in range(1, len(values)):
        for quality_indices in combinations(indices, quality_count):
            quality_set = set(quality_indices)
            ef_indices = tuple(i for i in indices if i not in quality_set)
            q_indices = tuple(quality_indices)
            ef_energy = sum(values[i] for i in ef_indices)
            quality_energy = sum(values[i] for i in q_indices)
            if ef_energy < quality_energy:
                continue

            affordable = []
            costs_by_name = {}
            for name in names:
                option = QUALITY_CATALOG[name]
                marker = getattr(state.profile, option.profile_attribute)
                costs_by_name[name] = quality_cost(marker, state.profile.ef)
                affordable.append(name)

            for count in range(len(affordable) + 1):
                for qualities in combinations(affordable, count):
                    costs = tuple((name, costs_by_name[name]) for name in qualities)
                    total_cost = sum(cost for _, cost in costs)
                    if total_cost > quality_energy:
                        continue
                    projected = projected_profile(state.profile, qualities)
                    if not projected["ef"] < projected["threshold"] < projected["vma"]:
                        continue
                    options.append(ProgramOption(
                        ef_indices=ef_indices,
                        quality_indices=q_indices,
                        ef_energy=ef_energy,
                        quality_energy=quality_energy,
                        qualities=tuple(qualities),
                        quality_costs=costs,
                        spec_remainder=quality_energy - total_cost,
                    ))

    return tuple(options)
