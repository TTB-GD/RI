#!/usr/bin/env python3
"""EXP R1-B controlled local-difficulty campaign."""

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
    from experiments.current.race_engine_v2.analysis_r1a2 import plausible_production_count
    from experiments.current.race_engine_v2.core import run_race
    from experiments.current.race_engine_v2.fixtures import (CTL_LEVEL, DIFFICULTY_PROFILES,
        POOLS, PRIMARY_PLAUSIBLE_MARGIN)
    from experiments.current.race_engine_v2.policies import POLICIES
else:
    from .analysis_r1a2 import plausible_production_count
    from .core import run_race
    from .fixtures import CTL_LEVEL, DIFFICULTY_PROFILES, POOLS, PRIMARY_PLAUSIBLE_MARGIN
    from .policies import POLICIES


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
R1B_POOLS = tuple(POOLS[name] for name in ("6d6", "4d8+1d6", "2d10+4d6", "1d8+3d6"))
POLICY_NAMES = ("EFFICIENT", "ADAPTIVE", "AGGRESSIVE", "GREEDY")


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def expected_form_control():
    with (RESULTS / "summary_r1a2.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    output = []
    for pool in R1B_POOLS:
        selected = [row for row in rows if row["form_mode"] == "PATTERN" and
                    row["sl"] == "False" and row["pool"] == pool.name]
        final_form = statistics.mean(float(row["mean_final_form"]) for row in selected)
        output.append({"pool": pool.name, "expected_form_signal": final_form / 3,
                       "expected_final_form": final_form})
    return output


def configs(phase):
    lengths = (6,) if phase == "smoke" else (6, 9)
    for pool, length, policy_name in product(R1B_POOLS, lengths, POLICY_NAMES):
        profiles = tuple(DIFFICULTY_PROFILES[length])
        for profile_name in profiles:
            yield pool, length, profile_name, policy_name


def execute(phase, seeds, output):
    grouped = {}
    course_path, turn_path = output / "courses_r1b.csv", output / "turns_r1b.csv"
    course_fields = ("seed", "pool", "length", "profile", "policy", "score", "dnf", "dnf_turn",
        "final_reserve", "spent", "reserve_remaining", "form_adjustment", "reserve_floor_clamped")
    turn_fields = ("seed", "pool", "length", "profile", "policy", "segment", "roll", "signal",
        "form_cumulative", "choice", "current_difficulty", "remaining_difficulty_profile",
        "physiological_load", "cost", "terrain_extra_cost", "spent", "reserve_remaining",
        "available", "payable", "reserve_floor_clamped")
    with course_path.open("w", newline="", encoding="utf-8") as cf, turn_path.open("w", newline="", encoding="utf-8") as tf:
        cw = csv.DictWriter(cf, fieldnames=course_fields, lineterminator="\n"); cw.writeheader()
        tw = csv.DictWriter(tf, fieldnames=turn_fields, lineterminator="\n"); tw.writeheader()
        for pool, length, profile_name, policy_name in configs(phase):
            profile = DIFFICULTY_PROFILES[length][profile_name]
            courses = []
            for seed in range(seeds):
                course = run_race(seed=seed, pool=pool, race_length=length, curve="B",
                    policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                    long_run_preparation=False, form_mode="PATTERN",
                    difficulty_profile=profile, profile_name=profile_name)
                courses.append(course)
                cw.writerow({field: course[field] for field in course_fields})
                for turn in course["turns"]:
                    row = {"seed": seed, "pool": pool.name, "length": length,
                        "profile": profile_name, "policy": policy_name,
                        "reserve_floor_clamped": course["reserve_floor_clamped"], **turn}
                    tw.writerow({field: json.dumps(row[field]) if isinstance(row[field], (tuple, list))
                                 else row[field] for field in turn_fields})
            grouped[(pool.name, length, profile_name, policy_name)] = courses
    return grouped


def validate_flat(grouped):
    fields = ("rolls", "signals", "form_adjustment", "raw_final_reserve", "final_reserve",
              "reserve_floor_clamped", "spent", "reserve_remaining", "score", "dnf", "dnf_turn")
    checked = 0
    for (pool_name, length, profile_name, policy_name), courses in grouped.items():
        if profile_name != "D0_FLAT":
            continue
        for flat in courses:
            baseline = run_race(seed=flat["seed"], pool=POOLS[pool_name], race_length=length,
                curve="B", policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                long_run_preparation=False, form_mode="PATTERN")
            if any(flat[field] != baseline[field] for field in fields):
                raise RuntimeError(f"D0 baseline divergence: {pool_name}/{length}/{policy_name}/{flat['seed']}")
            legacy_turn_fields = ("roll", "signal", "form_value", "form_cumulative", "available",
                                  "payable", "choice", "cost", "spent", "reserve_remaining")
            if any(tuple(turn[field] for field in legacy_turn_fields) !=
                   tuple(other[field] for field in legacy_turn_fields)
                   for turn, other in zip(flat["turns"], baseline["turns"])):
                raise RuntimeError(f"D0 turn divergence: {pool_name}/{length}/{policy_name}/{flat['seed']}")
            checked += 1
    return checked


def validate_committed_r1a2_flat(summaries):
    """Stop if comparable PATTERN D0 aggregates diverge from committed R1-A2."""
    with (RESULTS / "summary_r1a2.csv").open(encoding="utf-8") as handle:
        old_rows = list(csv.DictReader(handle))
    expected = {(row["pool"], int(row["length"]), row["policy"]): row for row in old_rows
                if row["form_mode"] == "PATTERN" and row["sl"] == "False"}
    checked = 0
    for row in summaries:
        if row["profile"] != "D0_FLAT" or row["policy"] == "AGGRESSIVE":
            continue  # AGGRESSIVE was not part of R1-A2.
        old = expected[(row["pool"], row["length"], row["policy"])]
        for field in ("mean_score", "median_score", "dnf_rate", "clamp_rate"):
            if abs(float(row[field]) - float(old[field])) > 1e-12:
                raise RuntimeError(f"committed R1-A2 D0 divergence: {row['pool']}/{row['length']}/{row['policy']}/{field}")
        checked += 1
    return checked


def course_metrics(course):
    turns = course["turns"]
    productions = [turn["choice"] for turn in turns]
    flat = [turn for turn in turns if turn["current_difficulty"] == 0]
    difficult = [turn for turn in turns if turn["current_difficulty"] > 0]
    split = len(productions) // 2
    first = statistics.mean(productions[:split]) if productions[:split] else 0
    second = statistics.mean(productions[split:]) if productions[split:] else 0
    return {
        "mean_production": statistics.mean(productions),
        "mean_production_flat": statistics.mean(t["choice"] for t in flat) if flat else float("nan"),
        "mean_production_difficult": statistics.mean(t["choice"] for t in difficult) if difficult else float("nan"),
        "mean_cost": statistics.mean(t["cost"] for t in turns),
        "mean_cost_flat": statistics.mean(t["cost"] for t in flat) if flat else float("nan"),
        "mean_cost_difficult": statistics.mean(t["cost"] for t in difficult) if difficult else float("nan"),
        "terrain_extra_cost": sum(t["terrain_extra_cost"] for t in turns),
        "available": statistics.mean(len(t["available"]) for t in turns),
        "payable": statistics.mean(len(t["payable"]) for t in turns),
        "plausible": statistics.mean(plausible_production_count(t["payable"], "B",
            PRIMARY_PLAUSIBLE_MARGIN, t["current_difficulty"]) for t in turns),
        "final_acceleration": len(productions) >= 3 and statistics.mean(productions[-2:]) > statistics.mean(productions[:-2]),
        "positive_split": second > first, "negative_split": second < first,
    }


def safe_mean(values):
    usable = [value for value in values if value == value]
    return statistics.mean(usable) if usable else ""


def summary_rows(grouped):
    rows = []
    for key, courses in grouped.items():
        pool, length, profile, policy = key
        metrics = [course_metrics(course) for course in courses]
        remaining = [course["reserve_remaining"] for course in courses if course["reserve_remaining"] is not None]
        rows.append({
            "pool": pool, "length": length, "profile": profile, "policy": policy, "seeds": len(courses),
            "mean_score": statistics.mean(c["score"] for c in courses),
            "median_score": statistics.median(c["score"] for c in courses),
            "dnf_rate": statistics.mean(c["dnf"] for c in courses),
            "mean_production": statistics.mean(m["mean_production"] for m in metrics),
            "mean_production_flat_segments": safe_mean(m["mean_production_flat"] for m in metrics),
            "mean_production_difficult_segments": safe_mean(m["mean_production_difficult"] for m in metrics),
            "mean_cost": statistics.mean(m["mean_cost"] for m in metrics),
            "mean_cost_flat_segments": safe_mean(m["mean_cost_flat"] for m in metrics),
            "mean_cost_difficult_segments": safe_mean(m["mean_cost_difficult"] for m in metrics),
            "mean_terrain_extra_cost": statistics.mean(m["terrain_extra_cost"] for m in metrics),
            "mean_spent": statistics.mean(c["spent"] for c in courses),
            "mean_reserve_remaining": statistics.mean(remaining),
            "clamp_rate": statistics.mean(c["reserve_floor_clamped"] for c in courses),
            "mean_available_productions": statistics.mean(m["available"] for m in metrics),
            "mean_payable_productions": statistics.mean(m["payable"] for m in metrics),
            "mean_plausible_productions": statistics.mean(m["plausible"] for m in metrics),
            "final_acceleration_rate": statistics.mean(m["final_acceleration"] for m in metrics),
            "positive_split_rate": statistics.mean(m["positive_split"] for m in metrics),
            "negative_split_rate": statistics.mean(m["negative_split"] for m in metrics),
        })
    return rows


def paired_values(flat, terrain, profile):
    difficult_indices = [i for i, value in enumerate(profile) if value > 0]
    common_difficult = [i for i in difficult_indices if i < len(flat["turns"]) and i < len(terrain["turns"])]
    difficult_delta = statistics.mean(terrain["turns"][i]["choice"] - flat["turns"][i]["choice"]
                                      for i in common_difficult) if common_difficult else float("nan")
    decisions = [terrain["turns"][i]["choice"] - flat["turns"][i]["choice"] for i in common_difficult]
    following = max(difficult_indices) + 1
    memory_delta = (terrain["turns"][following]["choice"] - flat["turns"][following]["choice"]
                    if following < len(profile) and following < len(flat["turns"]) and following < len(terrain["turns"])
                    else float("nan"))
    memory_reserve = (terrain["turns"][following]["reserve_remaining"] - flat["turns"][following]["reserve_remaining"]
                      if following < len(profile) and following < len(flat["turns"]) and following < len(terrain["turns"])
                      else float("nan"))
    return {
        "delta_difficult_production": difficult_delta,
        "slow_count": sum(delta <= -2 for delta in decisions),
        "maintain_count": sum(abs(delta) <= 1 for delta in decisions),
        "attack_count": sum(delta >= 2 for delta in decisions),
        "decision_count": len(decisions),
        "post_difficulty_production_delta": memory_delta,
        "post_difficulty_reserve_delta": memory_reserve,
    }


def terrain_comparisons(grouped):
    rows = []
    for pool in R1B_POOLS:
        for length in (6, 9):
            for policy in POLICY_NAMES:
                flat = grouped[(pool.name, length, "D0_FLAT", policy)]
                for profile_name in ("D1_EARLY", "D2_LATE"):
                    terrain = grouped[(pool.name, length, profile_name, policy)]
                    profile = DIFFICULTY_PROFILES[length][profile_name]
                    categories = ("ALL", "NEGATIVE", "ZERO", "POSITIVE") if policy == "ADAPTIVE" else ("ALL",)
                    for category in categories:
                        course_pairs = [(a, b) for a, b in zip(flat, terrain)
                            if category == "ALL" or form_group(a["form_adjustment"]) == category]
                        if not course_pairs:
                            continue
                        pairs = [paired_values(a, b, profile) for a, b in course_pairs]
                        total_decisions = sum(pair["decision_count"] for pair in pairs)
                        rows.append({
                            "pool": pool.name, "length": length, "policy": policy, "form_group": category,
                            "comparison": f"D0_FLAT_vs_{profile_name}", "pairs": len(pairs),
                            "mean_delta_difficult_production": safe_mean(p["delta_difficult_production"] for p in pairs),
                            "mean_delta_score": statistics.mean(b["score"] - a["score"] for a, b in course_pairs),
                            "mean_delta_cost": statistics.mean(sum(t["cost"] for t in b["turns"]) - sum(t["cost"] for t in a["turns"])
                                                                  for a, b in course_pairs),
                            "mean_delta_spent": statistics.mean(b["spent"] - a["spent"] for a, b in course_pairs),
                            "delta_dnf_rate": statistics.mean(b["dnf"] for a, b in course_pairs) - statistics.mean(a["dnf"] for a, b in course_pairs),
                            "mean_delta_reserve_remaining": safe_mean((b["reserve_remaining"] - a["reserve_remaining"])
                                for a, b in course_pairs if a["reserve_remaining"] is not None and b["reserve_remaining"] is not None),
                            "mean_terrain_extra_cost": statistics.mean(sum(t["terrain_extra_cost"] for t in b["turns"]) for a, b in course_pairs),
                            "slow_rate": sum(p["slow_count"] for p in pairs) / total_decisions if total_decisions else "",
                            "maintain_rate": sum(p["maintain_count"] for p in pairs) / total_decisions if total_decisions else "",
                            "attack_rate": sum(p["attack_count"] for p in pairs) / total_decisions if total_decisions else "",
                            "mean_post_difficulty_production_delta": safe_mean(p["post_difficulty_production_delta"] for p in pairs),
                            "mean_post_difficulty_reserve_delta": safe_mean(p["post_difficulty_reserve_delta"] for p in pairs),
                        })
    return rows


def form_group(value):
    return "NEGATIVE" if value < 0 else "ZERO" if value == 0 else "POSITIVE"


def timing_comparisons(grouped):
    rows = []
    for pool in R1B_POOLS:
        for length in (6, 9):
            for policy in POLICY_NAMES:
                early = grouped[(pool.name, length, "D1_EARLY", policy)]
                late = grouped[(pool.name, length, "D2_LATE", policy)]
                categories = ("ALL", "NEGATIVE", "ZERO", "POSITIVE") if policy == "ADAPTIVE" else ("ALL",)
                for category in categories:
                    pairs = [(a, b) for a, b in zip(early, late)
                             if category == "ALL" or form_group(a["form_adjustment"]) == category]
                    if not pairs:
                        continue
                    turn_deltas = []
                    for segment in range(length):
                        values = [b["turns"][segment]["choice"] - a["turns"][segment]["choice"]
                                  for a, b in pairs if segment < len(a["turns"]) and segment < len(b["turns"])]
                        turn_deltas.append(statistics.mean(values) if values else None)
                    rows.append({
                        "pool": pool.name, "length": length, "policy": policy, "form_group": category,
                        "pairs": len(pairs), "mean_delta_score_late_minus_early": statistics.mean(b["score"] - a["score"] for a, b in pairs),
                        "delta_dnf_rate_late_minus_early": statistics.mean(b["dnf"] for a, b in pairs) - statistics.mean(a["dnf"] for a, b in pairs),
                        "mean_delta_production_late_minus_early": statistics.mean(
                            statistics.mean(t["choice"] for t in b["turns"]) - statistics.mean(t["choice"] for t in a["turns"]) for a, b in pairs),
                        "mean_delta_spent_late_minus_early": statistics.mean(b["spent"] - a["spent"] for a, b in pairs),
                        "mean_delta_reserve_late_minus_early": safe_mean((b["reserve_remaining"] - a["reserve_remaining"])
                            for a, b in pairs if a["reserve_remaining"] is not None and b["reserve_remaining"] is not None),
                        "mean_delta_terrain_extra_cost_late_minus_early": statistics.mean(
                            sum(t["terrain_extra_cost"] for t in b["turns"]) - sum(t["terrain_extra_cost"] for t in a["turns"]) for a, b in pairs),
                        "turn_production_delta_late_minus_early": json.dumps(turn_deltas),
                    })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("smoke", "main"), default="main")
    parser.add_argument("--seeds", type=int)
    parser.add_argument("--output", type=Path, default=RESULTS)
    args = parser.parse_args()
    seeds = args.seeds or (50 if args.phase == "smoke" else 500)
    args.output.mkdir(parents=True, exist_ok=True)
    form_control = expected_form_control()
    started = time.perf_counter()
    grouped = execute(args.phase, seeds, args.output)
    flat_checked = validate_flat(grouped)
    summaries = summary_rows(grouped)
    committed_checked = validate_committed_r1a2_flat(summaries) if seeds == 500 else 0
    write_csv(args.output / "summary_r1b.csv", summaries)
    if args.phase == "main":
        write_csv(args.output / "terrain_comparison.csv", terrain_comparisons(grouped))
        write_csv(args.output / "timing_comparison.csv", timing_comparisons(grouped))
    metadata = {
        "experiment": "EXP R1-B LOCAL DIFFICULTY", "status": "EXPERIMENTAL ONLY",
        "phase": args.phase, "seeds": seeds, "seed_range": f"0..{seeds - 1}",
        "configuration_count": len(grouped), "course_count": len(grouped) * seeds,
        "form_mode": "PATTERN", "curve": "B", "ctl": CTL_LEVEL, "freshness": 0, "sl": False,
        "pools": [pool.name for pool in R1B_POOLS], "profiles": DIFFICULTY_PROFILES,
        "policies": list(POLICY_NAMES), "expected_form_control_from_r1a2": form_control,
        "flat_baseline_courses_checked": flat_checked, "runtime_seconds": time.perf_counter() - started,
        "committed_r1a2_summary_rows_checked": committed_checked,
        "maintain_convention": "paired difficult-turn delta -1..+1; SLOW <= -2; ATTACK >= +2",
        "plausible_efficiency_margin": PRIMARY_PLAUSIBLE_MARGIN,
        "baseline_git_head_at_run": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True).stdout.strip(),
        "large_ignored_outputs": ["courses_r1b.csv", "turns_r1b.csv"],
    }
    (args.output / "run_metadata_r1b.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
