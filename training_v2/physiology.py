"""Two-coordinate physiological curve used by Training B and Race.

The curve is an energy-to-speed mapping. Numerical milestone deltas are
configuration, not calibrated design constants.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


TRACKS = ("ef", "threshold", "vma")
CHOICES = ("speed", "economy")


@dataclass(frozen=True)
class PhysiologyPoint:
    energy: float
    speed: float

    def __post_init__(self):
        for name, value in (("energy", self.energy), ("speed", self.speed)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class PhysiologyCurve:
    """Three ordered landmarks in energy/speed space."""

    ef: PhysiologyPoint
    threshold: PhysiologyPoint
    vma: PhysiologyPoint

    def __post_init__(self):
        self.validate()

    def validate(self):
        points = (self.ef, self.threshold, self.vma)
        if not all(isinstance(point, PhysiologyPoint) for point in points):
            raise ValueError("EF, threshold and VMA must be PhysiologyPoint values")
        if not (
            self.ef.energy < self.threshold.energy < self.vma.energy
            and self.ef.speed < self.threshold.speed < self.vma.speed
        ):
            raise ValueError(
                "physiology curve must be strictly increasing in both energy and speed"
            )

    @property
    def max_race_energy(self) -> float:
        """Maximum energy spend allowed in Race: the VMA energy coordinate."""
        return self.vma.energy

    def point(self, track: str) -> PhysiologyPoint:
        if track not in TRACKS:
            raise ValueError(f"unknown physiology track: {track}")
        return getattr(self, track)

    def upgraded(self, track: str, choice: str, amount: float) -> "PhysiologyCurve":
        """Return a validated profile after one single-coordinate milestone choice."""
        if track not in TRACKS:
            raise ValueError(f"unknown physiology track: {track}")
        if choice not in CHOICES:
            raise ValueError(f"choice must be one of {CHOICES}")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("upgrade amount must be numeric")
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("upgrade amount must be finite and positive")

        old = self.point(track)
        updated = (
            PhysiologyPoint(old.energy, old.speed + amount)
            if choice == "speed"
            else PhysiologyPoint(old.energy - amount, old.speed)
        )
        values = {name: self.point(name) for name in TRACKS}
        values[track] = updated
        return PhysiologyCurve(**values)

    def available_choices(self, track: str, *, speed_gain: float,
                          energy_reduction: float) -> tuple[str, ...]:
        """Return only upgrades that preserve strict EF < Seuil < VMA ordering."""
        available = []
        for choice, amount in (
            ("speed", speed_gain),
            ("economy", energy_reduction),
        ):
            try:
                self.upgraded(track, choice, amount)
            except ValueError:
                continue
            available.append(choice)
        return tuple(available)
