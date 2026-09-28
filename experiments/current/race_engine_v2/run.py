#!/usr/bin/env python3
"""Reproducible smoke and targeted R1-A1 campaigns."""

import argparse
import csv
import json
from collections import defaultdict
from itertools import product
from pathlib import Path
import statistics
import subprocess
import time

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from experiments.current.race_engine_v2.core import available_productions, run_race
    from experiments.current.race_engine_v2.fixtures import (CTL_LEVEL, ENERGY_TABLES,
        FRESHNESS_LEVELS, POOLS, PRIORITY_POOLS, RACE_LENGTHS)
    from experiments.current.race_engine_v2.form import (classify_form_pattern,
        exact_sum_distribution, form_thresholds)
    from experiments.current.race_engine_v2.policies import POLICIES
else:
    from .core import available_productions, run_race
    from .fixtures import (CTL_LEVEL, ENERGY_TABLES, FRESHNESS_LEVELS, POOLS,
        PRIORITY_POOLS, RACE_LENGTHS)
    from .form import classify_form_pattern, exact_sum_distribution, form_thresholds
    from .policies import POLICIES


ROOT = Path(__file__).parent
SUMMARY_FIELDS = (
    "campaign", "pool", "length", "curve", "policy", "sl", "freshness", "ctl",
    "base_reserve", "seeds", "mean_score", "median_score", "dnf_rate",
    "mean_reserve_spent", "mean_reserve_remaining", "clamp_rate", "mean_production",
    "production_variance", "production_range", "costly_zone_frequency",
    "mean_choices_available", "mean_choices_payable", "positive_split_rate",
    "negative_split_rate", "final_acceleration_rate",
)


def smoke_configs():
    for pool, length, policy in product(PRIORITY_POOLS, RACE_LENGTHS, ("EFFICIENT", "ADAPTIVE", "GREEDY")):
        yield "R1-A0", pool, length, "B", policy, False, 0


def main_configs():
    # A: curve contrast, all pools, neutral preparation.
    for pool, length, curve, policy in product(POOLS.values(), RACE_LENGTHS, ENERGY_TABLES, POLICIES):
        yield "R1-A1_CURVES_POOLS", pool, length, curve, policy, False, 0
    # B: isolate SL on Curve B.
    for pool, length, policy in product(POOLS.values(), RACE_LENGTHS, POLICIES):
        yield "R1-A1_SL", pool, length, "B", policy, True, 0
    # C: isolate the one positive freshness fixture on Curve B, SL off.
    for pool, length, policy in product(POOLS.values(), RACE_LENGTHS, POLICIES):
        yield "R1-A1_FRESHNESS", pool, length, "B", policy, False, FRESHNESS_LEVELS[1]


def course_metrics(course):
    productions = [turn["choice"] for turn in course["turns"]]
    costs = [turn["cost"] for turn in course["turns"]]
    split = len(productions) // 2
    first = statistics.mean(productions[:split]) if split else 0
    second = statistics.mean(productions[split:]) if productions[split:] else 0
    prior = productions[:-2]
    return {
        "mean_production": statistics.mean(productions) if productions else 0,
        "production_variance": statistics.pvariance(productions) if productions else 0,
        "production_range": max(productions) - min(productions) if productions else 0,
        "costly_zone_frequency": sum(c >= 5 for c in costs) / len(costs) if costs else 0,
        "mean_choices_available": statistics.mean(len(t["available"]) for t in course["turns"]) if productions else 0,
        "mean_choices_payable": statistics.mean(len(t["payable"]) for t in course["turns"]) if productions else 0,
        "positive_split": second > first,
        "negative_split": second < first,
        "final_acceleration": len(productions) >= 3 and statistics.mean(productions[-2:]) > statistics.mean(prior),
        "cost_per_point": sum(costs) / sum(productions) if productions else 0,
        "spent_before_s3": course["turns"][1]["spent"] / course["final_reserve"] if len(course["turns"]) > 1 and course["final_reserve"] else 0,
        "spent_last_third": sum(costs[-max(1, course["length"] // 3):]) / course["final_reserve"] if costs and course["final_reserve"] else 0,
    }


def aggregate(campaign, courses):
    metrics = [course_metrics(c) for c in courses]
    productions = [t["choice"] for c in courses for t in c["turns"]]
    first = courses[0]
    remaining = [c["reserve_remaining"] for c in courses if c["reserve_remaining"] is not None]
    avg = lambda key: statistics.mean(m[key] for m in metrics)
    return {
        "campaign": campaign, "pool": first["pool"], "length": first["length"],
        "curve": first["curve"], "policy": first["policy"],
        "sl": first["long_run_preparation"], "freshness": first["freshness_bonus"],
        "ctl": first["ctl"], "base_reserve": first["base_reserve"], "seeds": len(courses),
        "mean_score": statistics.mean(c["score"] for c in courses),
        "median_score": statistics.median(c["score"] for c in courses),
        "dnf_rate": statistics.mean(c["dnf"] for c in courses),
        "mean_reserve_spent": statistics.mean(c["spent"] for c in courses),
        "mean_reserve_remaining": statistics.mean(remaining),
        "clamp_rate": statistics.mean(c["reserve_floor_clamped"] for c in courses),
        "mean_production": statistics.mean(productions),
        "production_variance": statistics.pvariance(productions),
        "production_range": max(productions) - min(productions),
        "costly_zone_frequency": avg("costly_zone_frequency"),
        "mean_choices_available": avg("mean_choices_available"),
        "mean_choices_payable": avg("mean_choices_payable"),
        "positive_split_rate": avg("positive_split"),
        "negative_split_rate": avg("negative_split"),
        "final_acceleration_rate": avg("final_acceleration"),
    }


def pattern_rows():
    rows = []
    for pool in POOLS.values():
        counts = exact_sum_distribution(pool.dice)
        totals = sum(counts.values())
        classes = defaultdict(int)
        # Classification depends only on total; weight every exact outcome.
        representative = {total: next((roll for roll in _rolls(pool.dice) if sum(roll) == total), None) for total in counts}
        for total, count in counts.items():
            classes[classify_form_pattern(representative[total], pool)] += count
        rows.append({
            "pool": pool.name, "method": "exact full-roll sum quantiles",
            "outcomes": totals, "low_frequency": classes["LOW"] / totals,
            "normal_frequency": classes["NORMAL"] / totals,
            "good_frequency": classes["GOOD"] / totals,
            "exceptional_frequency": classes["EXCEPTIONAL"] / totals,
            "thresholds": "/".join(map(str, form_thresholds(pool.dice))),
        })
    return rows


def _rolls(dice):
    from itertools import product as cartesian
    return cartesian(*(range(1, size + 1) for size in dice))


def granularity_stats():
    result = {}
    for pool in POOLS.values():
        availability = defaultdict(int)
        choices = []
        min_values, max_values = [], []
        exact_target = defaultdict(int)
        near1 = defaultdict(int)
        near2 = defaultdict(int)
        outcomes = 0
        for roll in _rolls(pool.dice):
            outcomes += 1
            productions = available_productions(roll).productions
            choices.append(len(productions)); min_values.append(min(productions)); max_values.append(max(productions))
            available_set = set(productions)
            for value in productions: availability[value] += 1
            for target in range(18, 26):
                exact_target[target] += target in available_set
                near1[target] += any(abs(p - target) <= 1 for p in productions)
                near2[target] += any(abs(p - target) <= 2 for p in productions)
        result[pool.name] = {
            "composition": list(pool.dice), "provenance": pool.provenance,
            "dice_count": len(pool.dice), "expected_full_sum": pool.expected_total,
            "full_sum_variance": pool.variance, "theoretical_min": len(pool.dice),
            "theoretical_max": sum(pool.dice), "exact_roll_outcomes": outcomes,
            "mean_distinct_productions": statistics.mean(choices),
            "mean_accessible_min": statistics.mean(min_values), "mean_accessible_max": statistics.mean(max_values),
            "production_availability_probability": {str(k): v / outcomes for k, v in sorted(availability.items())},
            "targets_18_25": {str(t): {"exact": exact_target[t] / outcomes, "plus_minus_1": near1[t] / outcomes,
                "plus_minus_2": near2[t] / outcomes} for t in range(18, 26)},
        }
    return result


def write_csv(path, rows, fields=None):
    if not rows:
        return
    fields = fields or tuple(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def execute(configs, seeds, course_writer, turn_writer):
    summaries = []
    for campaign, pool, length, curve, policy_name, sl, freshness in configs:
        courses = []
        for seed in range(seeds):
            course = run_race(seed=seed, pool=pool, race_length=length, curve=curve,
                policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=freshness,
                long_run_preparation=sl)
            courses.append(course)
            course_writer.writerow({k: course[k] for k in course_writer.fieldnames})
            for turn in course["turns"]:
                turn_writer.writerow({
                    "campaign": campaign, "seed": seed, "pool": pool.name, "length": length,
                    "curve": curve, "policy": policy_name, "sl": sl, "freshness": freshness,
                    **{k: json.dumps(v) if isinstance(v, (tuple, list)) else v for k, v in turn.items()},
                })
        summaries.append(aggregate(campaign, courses))
    return summaries


def validate_smoke(rows):
    grouped = defaultdict(set)
    for row in rows:
        grouped[(row["pool"], row["length"])].add(round(row["mean_score"], 6))
    if any(len(scores) < 2 for scores in grouped.values()):
        raise RuntimeError("structural smoke failure: policies do not diverge")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("smoke", "main", "all"), default="all")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    all_summaries = []
    course_fields = ("seed", "pool", "length", "curve", "policy", "long_run_preparation", "freshness_bonus",
        "ctl", "base_reserve", "form_adjustment", "raw_final_reserve", "final_reserve", "reserve_floor_clamped",
        "spent", "reserve_remaining", "score", "dnf", "dnf_turn")
    turn_fields = ("campaign", "seed", "pool", "length", "curve", "policy", "sl", "freshness", "segment", "roll",
        "signal", "form_value", "form_cumulative", "available", "payable", "choice", "cost", "spent", "reserve_remaining")
    with (args.output / "courses.csv").open("w", newline="", encoding="utf-8") as cf, (args.output / "turns.csv").open("w", newline="", encoding="utf-8") as tf:
        cw = csv.DictWriter(cf, fieldnames=course_fields, lineterminator="\n"); cw.writeheader()
        tw = csv.DictWriter(tf, fieldnames=turn_fields, lineterminator="\n"); tw.writeheader()
        if args.phase in ("smoke", "all"):
            smoke = execute(smoke_configs(), 50, cw, tw)
            validate_smoke(smoke)
            all_summaries.extend(smoke)
        if args.phase in ("main", "all"):
            all_summaries.extend(execute(main_configs(), 500, cw, tw))
    write_csv(args.output / "summary.csv", all_summaries, SUMMARY_FIELDS)
    write_csv(args.output / "pattern_stats.csv", pattern_rows())
    (args.output / "granularity_stats.json").write_text(json.dumps(granularity_stats(), indent=2, sort_keys=True) + "\n")
    elapsed = time.perf_counter() - started
    metadata = {
        "experiment": "EXP R1-A Race Engine V2 / flat terrain", "status": "EXPERIMENTAL ONLY",
        "phase": args.phase, "seed_ranges": {"R1-A0": "0..49", "R1-A1": "0..499"},
        "configuration_count": len(all_summaries), "course_count": sum(int(r["seeds"]) for r in all_summaries),
        "runtime_seconds": elapsed, "ctl_fixture": CTL_LEVEL, "freshness_fixtures": FRESHNESS_LEVELS,
        "curves": ENERGY_TABLES, "git_head_at_run": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            text=True, capture_output=True, check=True).stdout.strip(),
        "large_outputs": ["courses.csv", "turns.csv"],
    }
    (args.output / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
