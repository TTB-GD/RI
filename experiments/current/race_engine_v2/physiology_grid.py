"""Integer energy-to-speed grid for the Training B physiology curve.

The player board displays the integer-energy cells from zero through VMA.
Values outside that printed range are linearly extrapolated using the nearest
end segment. Terrain modifies effective energy, never the reserve expenditure.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from training_v2.physiology import PhysiologyCurve, TRACKS


@dataclass(frozen=True)
class GridCell:
    energy: int
    speed: int


@dataclass(frozen=True)
class RaceSegmentResult:
    energy_spent: int
    difficulty: int
    effective_energy: int
    speed: int
    reserve_remaining: int


@dataclass(frozen=True)
class PhysiologyGrid:
    """Printed integer lookup table backed by the player's three anchors."""

    cells: tuple[GridCell, ...]
    curve: PhysiologyCurve

    def __post_init__(self):
        if not self.cells:
            raise ValueError("physiology grid cannot be empty")
        if tuple(cell.energy for cell in self.cells) != tuple(range(len(self.cells))):
            raise ValueError("grid cells must cover consecutive energies starting at zero")

    def _unrounded_speed(self, energy: float) -> float:
        points = tuple(self.curve.point(track) for track in TRACKS)
        if energy <= points[0].energy:
            left, right = points[0], points[1]
        elif energy >= points[-1].energy:
            left, right = points[-2], points[-1]
        else:
            left, right = next(
                (a, b) for a, b in zip(points, points[1:])
                if a.energy <= energy <= b.energy
            )
        slope = (right.speed - left.speed) / (right.energy - left.energy)
        return left.speed + (energy - left.energy) * slope

    def speed_at(self, effective_energy: int) -> int:
        """Read the grid, extrapolate outside it, and round half up to an integer."""
        if isinstance(effective_energy, bool) or not isinstance(effective_energy, int):
            raise TypeError("effective energy must be an integer")
        # The displayed cells are the normal lookup. The same anchor rule extends
        # the first/last segment when terrain pushes energy outside the table.
        if 0 <= effective_energy < len(self.cells):
            return self.cells[effective_energy].speed
        raw_speed = self._unrounded_speed(effective_energy)
        return max(0, math.floor(raw_speed + 0.5))


def build_physiology_grid(curve: PhysiologyCurve) -> PhysiologyGrid:
    """Build board cells for integer energy values from zero through floor(VMA)."""
    if not isinstance(curve, PhysiologyCurve):
        raise TypeError("curve must be a PhysiologyCurve")
    max_energy = math.floor(curve.max_race_energy)
    cells = tuple(
        GridCell(energy, max(0, math.floor(
            # Half-up rounding; Python's round() uses ties-to-even.
            _interpolate(curve, energy) + 0.5
        )))
        for energy in range(max_energy + 1)
    )
    return PhysiologyGrid(cells=cells, curve=curve)


def _interpolate(curve: PhysiologyCurve, energy: float) -> float:
    points = tuple(curve.point(track) for track in TRACKS)
    if energy <= points[0].energy:
        left, right = points[0], points[1]
    elif energy >= points[-1].energy:
        left, right = points[-2], points[-1]
    else:
        left, right = next(
            (a, b) for a, b in zip(points, points[1:])
            if a.energy <= energy <= b.energy
        )
    slope = (right.speed - left.speed) / (right.energy - left.energy)
    return left.speed + (energy - left.energy) * slope


def resolve_race_segment(
    *,
    grid: PhysiologyGrid,
    energy_result: int,
    difficulty: int,
    reserve_remaining: int,
) -> RaceSegmentResult:
    """Clip the dice result to VMA, debit reserve, then convert through terrain.

    Positive difficulty is uphill; negative difficulty is downhill. The dice
    result is clipped to the VMA energy ceiling before checking/debiting reserve.
    Terrain correction never changes the actual reserve expenditure.
    """
    for name, value in (
        ("energy_result", energy_result),
        ("difficulty", difficulty),
        ("reserve_remaining", reserve_remaining),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if energy_result <= 0:
        raise ValueError("energy_result must be positive")
    # VMA is a hard clipping threshold, not a failure condition.
    energy_spent = min(energy_result, math.floor(grid.curve.max_race_energy))
    if reserve_remaining < energy_spent:
        raise ValueError("clipped energy expenditure exceeds remaining race reserve")

    effective_energy = energy_spent - difficulty
    speed = grid.speed_at(effective_energy)
    return RaceSegmentResult(
        energy_spent=energy_spent,
        difficulty=difficulty,
        effective_energy=effective_energy,
        speed=speed,
        reserve_remaining=reserve_remaining - energy_spent,
    )
