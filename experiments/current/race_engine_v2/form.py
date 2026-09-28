"""Pool-relative, exact and reproducible R1-A form classifications."""

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from .fixtures import FORM_QUANTILE_TARGETS, FORM_VALUES, DicePool


@lru_cache(maxsize=None)
def exact_sum_distribution(dice: tuple[int, ...]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for roll in product(*(range(1, size + 1) for size in dice)):
        total = sum(roll)
        counts[total] = counts.get(total, 0) + 1
    return counts


@lru_cache(maxsize=None)
def form_thresholds(dice: tuple[int, ...]) -> tuple[int, int, int]:
    counts = exact_sum_distribution(dice)
    outcomes = sum(counts.values())
    thresholds = []
    cumulative = 0
    target_index = 0
    for total, count in sorted(counts.items()):
        cumulative += count
        while target_index < len(FORM_QUANTILE_TARGETS) and cumulative / outcomes >= FORM_QUANTILE_TARGETS[target_index]:
            thresholds.append(total)
            target_index += 1
    return tuple(thresholds)  # type: ignore[return-value]


@dataclass(frozen=True)
class PatternFeatures:
    max_multiplicity: int
    pair_groups: int
    repeated_groups: int
    has_triple: bool
    has_two_pairs: bool
    has_full_house: bool
    has_four_kind: bool
    max_run_length: int
    distinct_values: int


def pattern_features(roll: tuple[int, ...]) -> PatternFeatures:
    """Return structural-only features; die-face magnitudes are never summed."""
    if not roll:
        raise ValueError("roll must be non-empty")
    counts = Counter(roll)
    multiplicities = sorted(counts.values(), reverse=True)
    distinct = sorted(counts)
    run = best_run = 1
    for previous, current in zip(distinct, distinct[1:]):
        run = run + 1 if current == previous + 1 else 1
        best_run = max(best_run, run)
    return PatternFeatures(
        max_multiplicity=multiplicities[0],
        pair_groups=sum(value == 2 for value in multiplicities),
        repeated_groups=sum(value >= 2 for value in multiplicities),
        has_triple=any(value >= 3 for value in multiplicities),
        has_two_pairs=sum(value >= 2 for value in multiplicities) >= 2,
        has_full_house=3 in multiplicities and 2 in multiplicities,
        has_four_kind=any(value >= 4 for value in multiplicities),
        max_run_length=best_run,
        distinct_values=len(distinct),
    )


def structural_pattern_score(roll: tuple[int, ...], dice_pool: DicePool) -> int:
    """Compact experimental score using structure, never raw sum or policy."""
    _validate_roll(roll, dice_pool)
    f = pattern_features(roll)
    motif_points = (
        3 * (f.max_multiplicity - 1)
        + 2 * f.repeated_groups
        + 2 * int(f.has_two_pairs)
        + 3 * int(f.has_full_house)
        + 4 * int(f.has_four_kind)
        + 2 * max(0, f.max_run_length - 2)
    )
    # Packing only breaks coarse-score ties with structural features. It never
    # uses face magnitudes: motif points dominate, then run length and diversity.
    return motif_points * 100 + f.max_run_length * 10 + f.distinct_values


def _validate_roll(roll: tuple[int, ...], dice_pool: DicePool) -> None:
    if len(roll) != len(dice_pool.dice):
        raise ValueError("roll and pool sizes differ")
    if any(face < 1 or face > size for face, size in zip(roll, dice_pool.dice)):
        raise ValueError("roll contains an invalid raw face")


def classify_form_sum(roll: tuple[int, ...], dice_pool: DicePool) -> str:
    """Original R1-A raw-sum classifier, retained byte-for-byte in behaviour."""
    _validate_roll(roll, dice_pool)
    q_low, q_normal, q_good = form_thresholds(dice_pool.dice)
    total = sum(roll)
    if total <= q_low:
        return "LOW"
    if total <= q_normal:
        return "NORMAL"
    if total <= q_good:
        return "GOOD"
    return "EXCEPTIONAL"


@lru_cache(maxsize=None)
def exact_pattern_distribution(dice: tuple[int, ...]) -> dict[int, int]:
    pool = DicePool("normalization", dice, "internal exact normalization")
    counts: dict[int, int] = {}
    for roll in product(*(range(1, size + 1) for size in dice)):
        score = structural_pattern_score(roll, pool)
        counts[score] = counts.get(score, 0) + 1
    return counts


@lru_cache(maxsize=None)
def pattern_thresholds(dice: tuple[int, ...]) -> tuple[int, int, int]:
    """Attainable cut points nearest the 20/70/93% exact cumulative targets."""
    counts = exact_pattern_distribution(dice)
    outcomes = sum(counts.values())
    cumulative = 0
    candidates = []
    for score, count in sorted(counts.items()):
        cumulative += count
        candidates.append((score, cumulative / outcomes))
    return tuple(min(candidates, key=lambda item: (abs(item[1] - target), item[0]))[0]
                 for target in FORM_QUANTILE_TARGETS)  # type: ignore[return-value]


def classify_form_structure(roll: tuple[int, ...], dice_pool: DicePool) -> str:
    _validate_roll(roll, dice_pool)
    q_low, q_normal, q_good = pattern_thresholds(dice_pool.dice)
    score = structural_pattern_score(roll, dice_pool)
    if score <= q_low:
        return "LOW"
    if score <= q_normal:
        return "NORMAL"
    if score <= q_good:
        return "GOOD"
    return "EXCEPTIONAL"


def classify_form(roll: tuple[int, ...], dice_pool: DicePool, mode: str) -> str:
    if mode == "SUM":
        return classify_form_sum(roll, dice_pool)
    if mode == "PATTERN":
        return classify_form_structure(roll, dice_pool)
    raise ValueError(f"unknown form mode: {mode}")


# Backward-compatible R1-A name. It deliberately remains the SUM baseline.
classify_form_pattern = classify_form_sum


def form_value(signal_class: str, long_run_preparation: bool) -> int:
    if signal_class not in FORM_VALUES:
        raise ValueError(f"unknown form class: {signal_class}")
    if long_run_preparation and signal_class == "LOW":
        return 0
    return FORM_VALUES[signal_class]
