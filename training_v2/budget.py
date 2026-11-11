"""Conserved EF / Quality energy split for the Training B turn model.

This module deliberately models only the budget partition. Session-dose
allocation, adaptation values, RPE risk and fatigue remain separate rules.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingEnergyBudget:
    """Partition one turn's final dice energy into EF and Quality.

    Quality is then partitioned between Threshold (Seuil) and VMA. Every
    energy point belongs to exactly one of EF, Threshold or VMA.
    """

    total_energy: int
    ef_energy: int
    threshold_energy: int
    vma_energy: int

    def __post_init__(self) -> None:
        values = (
            self.total_energy,
            self.ef_energy,
            self.threshold_energy,
            self.vma_energy,
        )
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise TypeError("energy values must be integers")
        if any(value < 0 for value in values):
            raise ValueError("energy values cannot be negative")
        if self.ef_energy + self.threshold_energy + self.vma_energy != self.total_energy:
            raise ValueError(
                "EF + Threshold + VMA allocations must conserve total energy"
            )

    @property
    def quality_energy(self) -> int:
        """Total Quality budget, before its Threshold / VMA split."""
        return self.threshold_energy + self.vma_energy

    @classmethod
    def from_split(
        cls,
        *,
        total_energy: int,
        ef_energy: int,
        threshold_energy: int,
        vma_energy: int,
    ) -> "TrainingEnergyBudget":
        """Build and validate a complete three-way allocation."""
        return cls(
            total_energy=total_energy,
            ef_energy=ef_energy,
            threshold_energy=threshold_energy,
            vma_energy=vma_energy,
        )
