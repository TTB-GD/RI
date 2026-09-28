"""Small dependency-free analysis helpers for EXP R1-A2."""

import math
import statistics

from .core import production_cost


def pearson(xs, ys) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return numerator / denominator if denominator else float("nan")


def average_ranks(values) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        rank = (start + 1 + end) / 2
        for index, _ in ordered[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def spearman(xs, ys) -> float:
    return pearson(average_ranks(xs), average_ranks(ys))


def correlation_pair(xs, ys) -> tuple[float, float]:
    return pearson(xs, ys), spearman(xs, ys)


def plausible_production_count(payable, curve: str, relative_margin: float,
                               difficulty: int = 0) -> int:
    """Diagnostic efficiency window; it is never consumed by a policy."""
    if not payable:
        return 0
    efficiencies = [production / production_cost(production, difficulty, curve) for production in payable]
    threshold = max(efficiencies) * (1 - relative_margin)
    return sum(value >= threshold for value in efficiencies)
