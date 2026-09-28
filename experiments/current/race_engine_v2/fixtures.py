"""Centralised EXPERIMENTAL FIXTURES for R1-A (not CURRENT rules)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DicePool:
    name: str
    dice: tuple[int, ...]
    provenance: str

    @property
    def expected_total(self) -> float:
        return sum((s + 1) / 2 for s in self.dice)

    @property
    def variance(self) -> float:
        return sum((s * s - 1) / 12 for s in self.dice)


# The two additional pools are reachable under dice_progression.py: the first
# after one upgrade; the second after four concentrated upgrades and CTL 100.
POOLS = {
    "6d6": DicePool("6d6", (6, 6, 6, 6, 6, 6), "required priority pool; CTL 100, no upgrades"),
    "4d8+1d6": DicePool("4d8+1d6", (8, 8, 8, 8, 6), "required priority comparison fixture"),
    "2d10+4d6": DicePool("2d10+4d6", (10, 10, 6, 6, 6, 6), "required priority power fixture"),
    "1d8+3d6": DicePool("1d8+3d6", (8, 6, 6, 6), "reachable initial pool after one upgrade"),
    "1d12+1d8+4d6": DicePool(
        "1d12+1d8+4d6", (12, 8, 6, 6, 6, 6),
        "reachable at CTL 100 after four concentrated upgrades",
    ),
}
PRIORITY_POOLS = tuple(POOLS[name] for name in ("6d6", "4d8+1d6", "2d10+4d6"))

# Inclusive upper bound -> cost. The final row is the explicit >=27 convention.
# A and C are arbitrary EXPERIMENTAL FIXTURES, deliberately bracketing B.
ENERGY_TABLES = {
    "A": ((15, 1), (18, 2), (21, 2), (22, 3), (23, 4), (24, 5), (25, 7), (26, 9), (None, 12)),
    "B": ((15, 1), (18, 2), (21, 2), (22, 3), (23, 5), (24, 7), (25, 10), (26, 13), (None, 16)),
    "C": ((15, 1), (18, 2), (21, 3), (22, 5), (23, 8), (24, 12), (25, 16), (26, 20), (None, 25)),
}

FORM_VALUES = {"LOW": -1, "NORMAL": 0, "GOOD": 1, "EXCEPTIONAL": 2}
FORM_QUANTILE_TARGETS = (0.20, 0.70, 0.93)  # EXPERIMENTAL FIXTURE
RACE_LENGTHS = (6, 9)
CTL_LEVEL = 100
FRESHNESS_LEVELS = (0, 3)

# Explicit experimental mapping: enough for one cheap choice per segment plus
# a small CTL-dependent margin. It is frozen before campaign execution.
RESERVE_PARAMETERS = {"per_segment": 2, "ctl_step": 50, "reserve_per_step": 1}

# Diagnostic only: policies never read these efficiency windows.
PLAUSIBLE_EFFICIENCY_MARGINS = (0.05, 0.10, 0.20)
PRIMARY_PLAUSIBLE_MARGIN = 0.10

# R1-B EXPERIMENTAL FIXTURES. Profiles are fully public before the race.
DIFFICULTY_PROFILES = {
    6: {
        "D0_FLAT": (0, 0, 0, 0, 0, 0),
        "D1_EARLY": (0, 3, 3, 0, 0, 0),
        "D2_LATE": (0, 0, 0, 0, 3, 3),
    },
    9: {
        "D0_FLAT": (0, 0, 0, 0, 0, 0, 0, 0, 0),
        "D1_EARLY": (0, 3, 3, 0, 0, 0, 0, 0, 0),
        "D2_LATE": (0, 0, 0, 0, 0, 0, 3, 3, 0),
        "D3_ROLLING": (0, 2, 0, 3, 0, 2, 0, 3, 0),
    },
}
