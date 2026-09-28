"""Pure R1-A energy cost boundary."""

from .fixtures import ENERGY_TABLES


def energy_cost(production: int, curve: str) -> int:
    if production <= 0:
        raise ValueError("production must be positive")
    try:
        rows = ENERGY_TABLES[curve]
    except KeyError as exc:
        raise ValueError(f"unknown energy curve: {curve}") from exc
    for upper, cost in rows:
        if upper is None or production <= upper:
            return cost
    raise AssertionError("energy table must have an unbounded final row")
