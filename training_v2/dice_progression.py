"""Player-chosen permanent dice-pool progression for Training B.

No progression thresholds are defined here. A progression event may call
add_die() or upgrade_die() after its trigger has been designed and validated.
"""
from __future__ import annotations

DIE_SIZES = (6, 8, 10, 12)
MIN_POOL_SIZE = 4
MAX_POOL_SIZE = 6


def add_die(state) -> None:
    """Add one permanent d6, up to the six-dice pool limit."""
    if len(state.dice_pool) >= MAX_POOL_SIZE:
        raise ValueError("dice pool is already at its maximum size")
    state.dice_pool.append(6)
    state.dice_added += 1


def upgrade_die(state, index: int) -> None:
    """Permanently improve the player-selected die by exactly one size."""
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("die index must be an integer")
    if not 0 <= index < len(state.dice_pool):
        raise ValueError("die index is outside the pool")
    current = state.dice_pool[index]
    if current not in DIE_SIZES[:-1]:
        raise ValueError("d12 is already the maximum die size")
    state.dice_pool[index] = DIE_SIZES[DIE_SIZES.index(current) + 1]
    state.upgrades_used += 1
