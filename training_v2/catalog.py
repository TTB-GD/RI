"""Data-driven experimental Training B session catalogue.

The first B increment keeps the B2 cost boundary as an explicit experimental
parameter while making session family, load type, adaptations and specific
fatigue catalogue data. It is not a final balance or a CURRENT ruleset.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityOption:
    key: str
    label: str
    profile_attribute: str
    family: str
    load_type: str = "QUALITY"
    adaptations: tuple[tuple[str, int], ...] = ()
    energy_cost: int = 0
    rpe: int = 0
    fatigue: int = 0
    max_per_turn: int | None = 1

    def __post_init__(self):
        if self.load_type not in ("EF", "QUALITY"):
            raise ValueError("load_type must be EF or QUALITY")
        if self.max_per_turn is not None and self.max_per_turn < 1:
            raise ValueError("max_per_turn must be positive or None")
        if self.energy_cost < 0 or self.rpe < 0 or self.fatigue < 0:
            raise ValueError("energy_cost, rpe and fatigue must be non-negative")
        if any(amount < 0 for _, amount in self.adaptations):
            raise ValueError("adaptations must be non-negative")


QUALITY_CATALOG = {
    "SEUIL": QualityOption(
        key="SEUIL",
        label="Séance au seuil",
        profile_attribute="threshold",
        family="SEUIL",
        adaptations=(("threshold", 1),),
        energy_cost=4,
        rpe=4,
    ),
    "VMA": QualityOption(
        key="VMA",
        label="Séance VMA",
        profile_attribute="vma",
        family="VMA",
        adaptations=(("vma", 1),),
        energy_cost=5,
        rpe=5,
        fatigue=1,
    ),
}


def projected_profile(profile, qualities):
    """Return profile values after applying catalogue adaptations."""
    projected = {
        "ef": profile.ef,
        "threshold": profile.threshold,
        "vma": profile.vma,
    }
    for name in qualities:
        option = QUALITY_CATALOG[name]
        for attribute, amount in option.adaptations:
            projected[attribute] += amount
    return projected


def difficulty(marker: int) -> int:
    """Provisional difficulty boundary used by Training V2 B2."""
    if marker < 8:
        raise ValueError("quality marker must be at least 8")
    return min(5, 1 + (marker - 8) // 5)


def quality_cost(marker: int, ef: int) -> int:
    """Historical B2 experimental cost formula; not used by the B catalogue."""
    if marker <= ef:
        raise ValueError("quality marker must be above EF")
    return (marker - ef) + difficulty(marker)
