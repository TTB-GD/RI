#!/usr/bin/env python3
"""Controlled FORM_SUM versus FORM_PATTERN micro-experiment."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import statistics
import subprocess
import time

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from experiments.current.race_engine_v2.analysis_r1a2 import correlation_pair, plausible_production_count
    from experiments.current.race_engine_v2.core import available_productions, run_race
    from experiments.current.race_engine_v2.fixtures import (CTL_LEVEL, PLAUSIBLE_EFFICIENCY_MARGINS,
        PRIMARY_PLAUSIBLE_MARGIN, POOLS)
    from experiments.current.race_engine_v2.form import (classify_form, exact_pattern_distribution,
        pattern_features, pattern_thresholds, structural_pattern_score)
    from experiments.current.race_engine_v2.policies import POLICIES
else:
    from .analysis_r1a2 import correlation_pair, plausible_production_count
    from .core import available_productions, run_race
    from .fixtures import CTL_LEVEL, PLAUSIBLE_EFFICIENCY_MARGINS, PRIMARY_PLAUSIBLE_MARGIN, POOLS
    from .form import (classify_form, exact_pattern_distribution, pattern_features,
        pattern_thresholds, structural_pattern_score)
    from .policies import POLICIES


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
R1A2_POOLS = tuple(POOLS[name] for name in ("6d6", "4d8+1d6", "2d10+4d6", "1d8+3d6"))
MODES = ("SUM", "PATTERN")
POLICY_NAMES = ("ADAPTIVE", "EFFICIENT", "GREEDY")
SIGNAL_NUMERIC = {"LOW": -1, "NORMAL": 0, "GOOD": 1, "EXCEPTIONAL": 2}


def rolls(dice):
    return product(*(range(1, size + 1) for size in dice))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def r1a2_configs():
    return product(MODES, R1A2_POOLS, (6, 9), POLICY_NAMES, (False, True))


def signal_vectors(courses):
    signals, raw_sums, maxima, chosen = [], [], [], []
    for course in courses:
        for turn in course["turns"][:3]:
            signals.append(SIGNAL_NUMERIC[turn["signal"]])
            raw_sums.append(turn["raw_roll_sum"])
            maxima.append(turn["max_available_production"])
            chosen.append(turn["choice"])
    return signals, raw_sums, maxima, chosen


def aggregate_config(courses):
    first = courses[0]
    signals, raw_sums, maxima, chosen = signal_vectors(courses)
    signal_raw = correlation_pair(signals, raw_sums)
    signal_max = correlation_pair(signals, maxima)
    signal_chosen = correlation_pair(signals, chosen)
    final_forms = [course["form_adjustment"] for course in courses]
    scores = [course["score"] for course in courses]
    reserves = [course["final_reserve"] for course in courses]
    form_score = correlation_pair(final_forms, scores)
    form_reserve = correlation_pair(final_forms, reserves)
    turns = [turn for course in courses for turn in course["turns"]]
    plausible = {margin: [plausible_production_count(turn["payable"], "B", margin) for turn in turns]
                 for margin in PLAUSIBLE_EFFICIENCY_MARGINS}
    return {
        "form_mode": first["form_mode"], "pool": first["pool"], "length": first["length"],
        "policy": first["policy"], "sl": first["long_run_preparation"], "seeds": len(courses),
        "mean_score": statistics.mean(scores), "median_score": statistics.median(scores),
        "dnf_rate": statistics.mean(course["dnf"] for course in courses),
        "clamp_rate": statistics.mean(course["reserve_floor_clamped"] for course in courses),
        "mean_final_form": statistics.mean(final_forms), "mean_final_reserve": statistics.mean(reserves),
        "low_signal_frequency": signals.count(-1) / len(signals),
        "pearson_signal_raw_sum": signal_raw[0], "spearman_signal_raw_sum": signal_raw[1],
        "pearson_signal_max_production": signal_max[0], "spearman_signal_max_production": signal_max[1],
        "pearson_signal_chosen_production": signal_chosen[0], "spearman_signal_chosen_production": signal_chosen[1],
        "pearson_final_form_score": form_score[0], "spearman_final_form_score": form_score[1],
        "pearson_final_form_reserve": form_reserve[0], "spearman_final_form_reserve": form_reserve[1],
        "mean_plausible_count_margin_05": statistics.mean(plausible[0.05]),
        "mean_plausible_count_margin_10": statistics.mean(plausible[0.10]),
        "mean_plausible_count_margin_20": statistics.mean(plausible[0.20]),
        "mean_available_production_count": statistics.mean(len(turn["available"]) for turn in turns),
        "mean_payable_production_count": statistics.mean(len(turn["payable"]) for turn in turns),
    }


def correlation_rows(grouped_courses):
    rows = []
    for key, courses in grouped_courses.items():
        mode, pool, length, policy, sl = key
        signals, raw_sums, maxima, chosen = signal_vectors(courses)
        final_form = [course["form_adjustment"] for course in courses]
        score = [course["score"] for course in courses]
        reserve = [course["final_reserve"] for course in courses]
        for metric, xs, ys, level in (
            ("signal_raw_sum", signals, raw_sums, "signal"),
            ("signal_max_production", signals, maxima, "signal"),
            ("signal_chosen_production", signals, chosen, "signal"),
            ("final_form_score", final_form, score, "course"),
            ("final_form_final_reserve", final_form, reserve, "course"),
        ):
            pearson, spearman = correlation_pair(xs, ys)
            rows.append({"form_mode": mode, "scope": "configuration", "pool": pool,
                "length": length, "policy": policy, "sl": sl, "level": level,
                "metric": metric, "observations": len(xs), "pearson": pearson, "spearman": spearman})
    for mode in MODES:
        for pool_name in [pool.name for pool in R1A2_POOLS] + ["GLOBAL"]:
            selected = [course for key, values in grouped_courses.items() if key[0] == mode and
                        (pool_name == "GLOBAL" or key[1] == pool_name) for course in values]
            signals, raw_sums, maxima, chosen = signal_vectors(selected)
            final_form = [course["form_adjustment"] for course in selected]
            score = [course["score"] for course in selected]
            reserve = [course["final_reserve"] for course in selected]
            for metric, xs, ys, level in (
                ("signal_raw_sum", signals, raw_sums, "signal"),
                ("signal_max_production", signals, maxima, "signal"),
                ("signal_chosen_production", signals, chosen, "signal"),
                ("final_form_score", final_form, score, "course"),
                ("final_form_final_reserve", final_form, reserve, "course"),
            ):
                pearson, spearman = correlation_pair(xs, ys)
                rows.append({"form_mode": mode, "scope": "pool" if pool_name != "GLOBAL" else "global",
                    "pool": pool_name, "length": "ALL", "policy": "ALL", "sl": "ALL", "level": level,
                    "metric": metric, "observations": len(xs), "pearson": pearson, "spearman": spearman})
    return rows


def pattern_stats_rows():
    rows_out = []
    for pool in R1A2_POOLS:
        for mode in MODES:
            classes = Counter(); scores = Counter(); numeric = []; sums = []; maxima = []
            for roll in rolls(pool.dice):
                classification = classify_form(roll, pool, mode)
                classes[classification] += 1
                numeric.append(SIGNAL_NUMERIC[classification])
                sums.append(sum(roll))
                maxima.append(max(available_productions(roll).productions))
                if mode == "PATTERN":
                    scores[structural_pattern_score(roll, pool)] += 1
            total = len(numeric)
            corr_sum = correlation_pair(numeric, sums)
            corr_max = correlation_pair(numeric, maxima)
            rows_out.append({
                "form_mode": mode, "pool": pool.name,
                "method": "exact raw-sum quantiles" if mode == "SUM" else "exact structural-score normalization",
                "cases": total, "score_distribution": json.dumps(dict(sorted(scores.items()))) if scores else "not applicable",
                "thresholds": "sum baseline unchanged" if mode == "SUM" else "/".join(map(str, pattern_thresholds(pool.dice))),
                "low_frequency": classes["LOW"] / total, "normal_frequency": classes["NORMAL"] / total,
                "good_frequency": classes["GOOD"] / total, "exceptional_frequency": classes["EXCEPTIONAL"] / total,
                "pearson_class_raw_sum": corr_sum[0], "spearman_class_raw_sum": corr_sum[1],
                "pearson_class_max_production": corr_max[0], "spearman_class_max_production": corr_max[1],
            })
    return rows_out


def diagnostic_examples():
    examples = {}
    for pool in R1A2_POOLS:
        low_cut = pool.expected_total - 0.4 * (pool.variance ** 0.5)
        high_cut = pool.expected_total + 0.4 * (pool.variance ** 0.5)
        for roll in rolls(pool.dice):
            raw_sum = sum(roll)
            pattern_class = classify_form(roll, pool, "PATTERN")
            key = None
            if raw_sum <= low_cut and pattern_class in ("GOOD", "EXCEPTIONAL"):
                key = "low_sum_good_pattern"
            elif raw_sum >= high_cut and pattern_class in ("LOW", "NORMAL"):
                key = "high_sum_plain_pattern"
            elif raw_sum >= high_cut and pattern_class in ("GOOD", "EXCEPTIONAL"):
                key = "high_sum_good_pattern"
            elif raw_sum <= low_cut and pattern_class in ("LOW", "NORMAL"):
                key = "low_sum_plain_pattern"
            if key and key not in examples:
                options = available_productions(roll).productions
                examples[key] = {"pool": pool.name, "roll": roll, "raw_sum": raw_sum,
                    "features": pattern_features(roll).__dict__, "structural_score": structural_pattern_score(roll, pool),
                    "pattern_class": pattern_class, "sum_class": classify_form(roll, pool, "SUM"),
                    "accessible_productions": options}
            if len(examples) == 4:
                return examples
    return examples


def validate_sum_baseline(grouped):
    """Stop unless explicit SUM and default R1-A execution are identical."""
    fields = ("rolls", "signals", "form_values", "form_adjustment", "final_reserve",
              "reserve_floor_clamped", "score", "dnf", "dnf_turn", "turns")
    checked = 0
    for key, courses in grouped.items():
        mode, pool_name, length, policy_name, sl = key
        if mode != "SUM":
            continue
        pool = POOLS[pool_name]
        for expected in courses:
            actual = run_race(seed=expected["seed"], pool=pool, race_length=length, curve="B",
                policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                long_run_preparation=sl)
            if any(actual[field] != expected[field] for field in fields):
                raise RuntimeError(f"FORM_SUM baseline divergence: {key}, seed {expected['seed']}")
            checked += 1
    return checked


def validate_compact_r1a_baseline(summary_rows):
    """Compare SUM score/DNF/clamp against the committed R1-A aggregates."""
    baseline_path = RESULTS / "summary.csv"
    with baseline_path.open(encoding="utf-8") as handle:
        baseline = list(csv.DictReader(handle))
    expected = {}
    for row in baseline:
        if row["curve"] != "B" or row["freshness"] != "0":
            continue
        if row["campaign"] == "R1-A1_CURVES_POOLS" and row["sl"] == "False":
            expected[(row["pool"], int(row["length"]), row["policy"], False)] = row
        elif row["campaign"] == "R1-A1_SL" and row["sl"] == "True":
            expected[(row["pool"], int(row["length"]), row["policy"], True)] = row
    checked = 0
    for row in summary_rows:
        if row["form_mode"] != "SUM":
            continue
        key = (row["pool"], row["length"], row["policy"], row["sl"])
        old = expected[key]
        for new_field, old_field in (("mean_score", "mean_score"), ("median_score", "median_score"),
                                     ("dnf_rate", "dnf_rate"), ("clamp_rate", "clamp_rate")):
            if abs(float(row[new_field]) - float(old[old_field])) > 1e-12:
                raise RuntimeError(f"committed R1-A baseline divergence: {key}, {new_field}")
        checked += 1
    return checked


def run_campaign(seeds, detailed_output):
    grouped = {}
    with detailed_output.open("w", newline="", encoding="utf-8") as handle:
        fields = ("form_mode", "pool", "length", "policy", "sl", "seed", "segment", "roll",
            "raw_roll_sum", "structural_pattern_score", "signal", "choice", "cost", "spent",
            "final_form", "final_reserve", "score", "dnf", "clamp")
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader()
        for mode, pool, length, policy_name, sl in r1a2_configs():
            courses = []
            for seed in range(seeds):
                course = run_race(seed=seed, pool=pool, race_length=length, curve="B",
                    policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                    long_run_preparation=sl, form_mode=mode)
                courses.append(course)
                for turn in course["turns"]:
                    writer.writerow({"form_mode": mode, "pool": pool.name, "length": length,
                        "policy": policy_name, "sl": sl, "seed": seed, "segment": turn["segment"],
                        "roll": json.dumps(turn["roll"]), "raw_roll_sum": turn["raw_roll_sum"],
                        "structural_pattern_score": turn["structural_pattern_score"], "signal": turn["signal"],
                        "choice": turn["choice"], "cost": turn["cost"], "spent": turn["spent"],
                        "final_form": course["form_adjustment"], "final_reserve": course["final_reserve"],
                        "score": course["score"], "dnf": course["dnf"], "clamp": course["reserve_floor_clamped"]})
            grouped[(mode, pool.name, length, policy_name, sl)] = courses
    return grouped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=500)
    parser.add_argument("--output", type=Path, default=RESULTS)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    grouped = run_campaign(args.seeds, args.output / "turns_r1a2.csv")
    checked = validate_sum_baseline(grouped)
    summaries = [aggregate_config(courses) for courses in grouped.values()]
    compact_checked = validate_compact_r1a_baseline(summaries) if args.seeds == 500 else 0
    write_csv(args.output / "summary_r1a2.csv", summaries)
    write_csv(args.output / "correlations.csv", correlation_rows(grouped))
    write_csv(args.output / "pattern_stats_v2.csv", pattern_stats_rows())
    metadata = {
        "experiment": "EXP R1-A2 FORM PATTERN NORMALIZATION", "status": "EXPERIMENTAL ONLY",
        "seeds": args.seeds, "seed_range": f"0..{args.seeds - 1}", "configuration_count": len(grouped),
        "course_count": len(grouped) * args.seeds, "curve": "B", "freshness": 0,
        "pools": [pool.name for pool in R1A2_POOLS], "lengths": [6, 9],
        "policies": list(POLICY_NAMES), "sl": [False, True], "form_modes": list(MODES),
        "sum_baseline_courses_checked": checked, "plausible_efficiency_margins": PLAUSIBLE_EFFICIENCY_MARGINS,
        "committed_r1a_summary_rows_checked": compact_checked,
        "primary_plausible_margin": PRIMARY_PLAUSIBLE_MARGIN, "runtime_seconds": time.perf_counter() - started,
        "diagnostic_examples": diagnostic_examples(),
        "baseline_git_head_at_run": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True).stdout.strip(),
        "large_ignored_output": "turns_r1a2.csv",
    }
    (args.output / "run_metadata_r1a2.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({k: v for k, v in metadata.items() if k != "diagnostic_examples"}, indent=2))


if __name__ == "__main__":
    main()
