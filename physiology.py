"""Integrated V2 physiological profile and energy-cost rule.

The 2/3 slopes are an experimental calibration.  The profile structure is the
integrated boundary between future training work and Race V2.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysiologyProfile:
    """A runner's integrated physiological landmarks."""

    ef: int
    threshold: int
    vma: int

    def __post_init__(self) -> None:
        if not self.ef < self.threshold < self.vma:
            raise ValueError("physiology profile must satisfy ef < threshold < vma")


def physiological_cost(profile: PhysiologyProfile, load: int) -> int:
    """Return the experimental-calibration cost for a legal V2 load."""

    if load > profile.vma:
        raise ValueError("load above vma is outside the integrated V2 domain")
    if load <= profile.ef:
        return profile.ef
    if load <= profile.threshold:
        return profile.ef + 2 * (load - profile.ef)
    return (
        profile.ef
        + 2 * (profile.threshold - profile.ef)
        + 3 * (load - profile.threshold)
    )
