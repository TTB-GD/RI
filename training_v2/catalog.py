"""Small experimental Training V2 quality catalogue.

EF is the aerobic support compartment, not a selectable quality session.
The quality costs reproduce the B2 experimental boundary. The initial
catalogue intentionally contains only Seuil and VMA; SL and SPEC are deferred
until their acquisition and adaptation rules are specified end-to-end.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityOption:
    key: str
    label: str
    profile_attribute: str
    fatigue: int = 0


QUALITY_CATALOG = {
    "SEUIL": QualityOption(
        key="SEUIL", label="Séance au seuil", profile_attribute="threshold"
    ),
    "VMA": QualityOption(
        key="VMA", label="Séance VMA", profile_attribute="vma"
    ),
}


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
