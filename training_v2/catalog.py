"""Declarative Training B session catalogue (experimental fixtures)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionOption:
    key: str
    label: str
    family: str
    load_type: str
    adaptations: tuple[tuple[str, int], ...]
    energy_cost: int
    rpe: int
    fatigue: int = 0
    max_per_turn: int | None = 1

    def __post_init__(self):
        if self.load_type not in ("EF", "QUALITY"):
            raise ValueError("load_type must be EF or QUALITY")
        if self.energy_cost < 1 or self.rpe < 0 or self.fatigue < 0:
            raise ValueError("invalid session cost, RPE or fatigue")
        if self.max_per_turn is not None and self.max_per_turn < 1:
            raise ValueError("max_per_turn must be positive or None")
        if any(amount < 0 for _, amount in self.adaptations):
            raise ValueError("adaptations must be non-negative")


SESSION_CATALOG = {
    "EF": SessionOption(
        key="EF", label="EF fondamentale", family="EF", load_type="EF",
        adaptations=(("ef", 1),), energy_cost=2, rpe=2,
        max_per_turn=None,
    ),
    "SEUIL": SessionOption(
        key="SEUIL", label="Tempo au seuil", family="SEUIL",
        load_type="QUALITY", adaptations=(("threshold", 1),),
        energy_cost=4, rpe=4,
    ),
    "VMA": SessionOption(
        key="VMA", label="Fractionné VMA", family="VMA",
        load_type="QUALITY", adaptations=(("vma", 1),),
        energy_cost=5, rpe=5, fatigue=1,
    ),
}


def projected_profile(profile, session_keys):
    projected = {"ef": profile.ef, "threshold": profile.threshold, "vma": profile.vma}
    for key in session_keys:
        for attribute, amount in SESSION_CATALOG[key].adaptations:
            projected[attribute] += amount
    return projected


def difficulty(marker: int) -> int:
    """Historical B2 reference helper; not used by active sessions."""
    if marker < 8:
        raise ValueError("quality marker must be at least 8")
    return min(5, 1 + (marker - 8) // 5)


def quality_cost(marker: int, ef: int) -> int:
    """Historical B2 reference helper; not used by active sessions."""
    if marker <= ef:
        raise ValueError("quality marker must be above EF")
    return (marker - ef) + difficulty(marker)
