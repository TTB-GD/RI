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
    fatigue: int = 0
    max_per_turn: int | None = 1

    def __post_init__(self):
        if self.load_type not in ("EF", "QUALITY"):
            raise ValueError("load_type must be EF or QUALITY")
        if self.max_per_turn is not None and self.max_per_turn < 1:
            raise ValueError("max_per_turn must be positive or None")
        if any(amount < 0 for _, amount in self.adaptations):
            raise ValueError("adaptations must be non-negative")


QUALITY_CATALOG = {
    "SEUIL": QualityOption(
        key="SEUIL",
        label="Séance au seuil",
        profile_attribute="threshold",
        family="SEUIL",
        adaptations=(("threshold", 1),),
    ),
    "VMA": QualityOption(
        key="VMA",
        label="Séance VMA",
        profile_attribute="vma",
        family="VMA",
        adaptations=(("vma", 1),),
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
    """B2 cost: marker gap plus the experimental difficulty surcharge."""
    if marker <= ef:
        raise ValueError("quality marker must be above EF")
    return (marker - ef) + difficulty(marker)
