"""Deterministic Race V2 sector resolution prototype.

The speed table is an explicit integer lookup supplied by the Training/profile
layer. This module deliberately does not interpolate or invent anchor values.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RacePhysiologyTable:
    """Integer energy -> speed lookup, indexed by energy from zero to VMA."""

    speeds: tuple[int, ...]
    ef_energy: int
    threshold_energy: int
    vma_energy: int

    def __post_init__(self) -> None:
        if not self.speeds:
            raise ValueError("speeds cannot be empty")
        if any(type(value) is not int or value < 0 for value in self.speeds):
            raise ValueError("all speeds must be non-negative integers")
        if not (
            type(self.ef_energy) is int
            and type(self.threshold_energy) is int
            and type(self.vma_energy) is int
            and 0 <= self.ef_energy < self.threshold_energy < self.vma_energy
        ):
            raise ValueError("energy anchors must satisfy 0 <= EF < Seuil < VMA")
        if len(self.speeds) != self.vma_energy + 1:
            raise ValueError("speeds must provide one cell for every energy 0..VMA")
        if any(a > b for a, b in zip(self.speeds, self.speeds[1:])):
            raise ValueError("speed table must be non-decreasing")
        if not (
            self.speeds[self.ef_energy]
            < self.speeds[self.threshold_energy]
            < self.speeds[self.vma_energy]
        ):
            raise ValueError("anchor speeds must satisfy EF < Seuil < VMA")

    @property
    def ef_speed(self) -> int:
        return self.speeds[self.ef_energy]


@dataclass(frozen=True)
class SectorResolution:
    energy_spent: int
    conversion_energy: int
    effective_curve_energy: int
    speed: int
    sustainability_consumption: int
    degradation_used: int
    degradation_next: int
    reserve_next: int
    cumulative_consumption_next: int


def sustainability_balance(
    *, initial_credit: int, cumulative_form: int, cumulative_consumption: int
) -> tuple[int, int]:
    """Return (degradation, reserve) from cumulative Race V2 balances."""
    if type(initial_credit) is not int or initial_credit < 0:
        raise ValueError("initial_credit must be a non-negative integer")
    if type(cumulative_form) is not int:
        raise ValueError("cumulative_form must be an integer")
    if type(cumulative_consumption) is not int or cumulative_consumption < 0:
        raise ValueError("cumulative_consumption must be a non-negative integer")

    available = initial_credit + cumulative_form
    degradation = max(0, cumulative_consumption - available)
    reserve = max(0, available - cumulative_consumption)
    return degradation, reserve


def _sector_consumption(energy_spent: int, specific_pace: int) -> int:
    if energy_spent == 0:
        return 0
    if energy_spent < specific_pace - 1:
        return 0
    if energy_spent <= specific_pace + 1:
        return 1
    return 2


def resolve_sector(
    *,
    table: RacePhysiologyTable,
    energy_result: int,
    group_bonus: int,
    terrain_difficulty: int,
    specific_pace: int,
    initial_credit: int,
    cumulative_form: int,
    cumulative_consumption: int,
) -> SectorResolution:
    """Resolve one sector using the Race V2 order of operations.

    energy_result is the sum of selected dice before the VMA expenditure cap.
    Positive terrain difficulty is uphill; negative is downhill. Group and
    terrain affect conversion only, never actual expenditure or sustainability.

    The incoming form total is assumed to include any card revealed at the
    beginning of this sector. Incoming consumption contains prior sectors only.
    Consumption generated here is committed after conversion and affects the
    next sector, not this one.
    """
    integer_inputs = {
        "energy_result": energy_result,
        "group_bonus": group_bonus,
        "terrain_difficulty": terrain_difficulty,
        "specific_pace": specific_pace,
        "initial_credit": initial_credit,
        "cumulative_form": cumulative_form,
        "cumulative_consumption": cumulative_consumption,
    }
    if any(type(value) is not int for value in integer_inputs.values()):
        raise TypeError("all sector inputs must be integers")
    if energy_result < 0:
        raise ValueError("energy_result cannot be negative")
    if group_bonus not in (0, 1):
        raise ValueError("group_bonus must be 0 or 1")
    if not 0 < specific_pace <= table.vma_energy:
        raise ValueError("specific_pace must be within the physiological energy range")

    energy_spent = min(energy_result, table.vma_energy)
    degradation_used, _ = sustainability_balance(
        initial_credit=initial_credit,
        cumulative_form=cumulative_form,
        cumulative_consumption=cumulative_consumption,
    )

    # Zero expenditure is a true no-op: neither group nor terrain can create
    # energy or speed, and the EF speed floor does not apply.
    if energy_spent == 0:
        conversion_energy = 0
        effective_curve_energy = table.ef_energy
        speed = 0
    else:
        conversion_energy = min(
            table.vma_energy,
            energy_spent + group_bonus - terrain_difficulty,
        )
        # A rightward curve shift means the same conversion energy reads an
        # earlier cell of the initial table. EF remains the speed floor.
        effective_curve_energy = max(
            table.ef_energy,
            min(table.vma_energy, conversion_energy - degradation_used),
        )
        speed = table.speeds[effective_curve_energy]

    sector_consumption = _sector_consumption(energy_spent, specific_pace)
    cumulative_consumption_next = cumulative_consumption + sector_consumption
    degradation_next, reserve_next = sustainability_balance(
        initial_credit=initial_credit,
        cumulative_form=cumulative_form,
        cumulative_consumption=cumulative_consumption_next,
    )

    return SectorResolution(
        energy_spent=energy_spent,
        conversion_energy=conversion_energy,
        effective_curve_energy=effective_curve_energy,
        speed=speed,
        sustainability_consumption=sector_consumption,
        degradation_used=degradation_used,
        degradation_next=degradation_next,
        reserve_next=reserve_next,
        cumulative_consumption_next=cumulative_consumption_next,
    )
