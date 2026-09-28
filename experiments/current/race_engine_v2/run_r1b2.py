#!/usr/bin/env python3
"""EXP R1-B2: controlled magnitude and frequency calibration."""

import argparse
import csv
import json
from collections import Counter
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
    from experiments.current.race_engine_v2.fixtures import CTL_LEVEL, POOLS, PRIMARY_PLAUSIBLE_MARGIN
    from experiments.current.race_engine_v2.policies import POLICIES
else:
    from .analysis_r1a2 import plausible_production_count
    from .core import run_race
    from .fixtures import CTL_LEVEL, POOLS, PRIMARY_PLAUSIBLE_MARGIN
    from .policies import POLICIES


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
POOLS_R1B2 = tuple(POOLS[name] for name in ("6d6", "4d8+1d6", "2d10+4d6", "1d8+3d6"))
POLICY_NAMES = ("EFFICIENT", "ADAPTIVE", "AGGRESSIVE", "GREEDY")
FLAT = (0,) * 9
MAGNITUDE_PROFILES = {"M0": FLAT, **{f"M{d}": (0, 0, 0, d, d, 0, 0, 0, 0) for d in range(1, 5)}}
REPRESENTATIVE_PROFILES = {
    "P0": FLAT,
    "P1": (0, 1, 0, 1, 0, 1, 0, 1, 0),
    "P2": (0, 0, 2, 0, 0, 2, 0, 0, 0),
    "P3": (0, 0, 3, 3, 0, 0, 0, 0, 0),
}


def frequency_profiles(magnitudes):
    output = {"F0": FLAT}
    for d in magnitudes:
        output.update({
            f"D{d}_F2": (0, d, 0, 0, 0, d, 0, 0, 0),
            f"D{d}_F3": (0, d, 0, 0, d, 0, 0, d, 0),
            f"D{d}_F4": (0, d, 0, d, 0, d, 0, d, 0),
        })
    return output


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def simulate(profiles, seeds, detail_prefix, output):
    grouped = {}
    courses_path = output / f"courses_r1b2_{detail_prefix}.csv"
    turns_path = output / f"turns_r1b2_{detail_prefix}.csv"
    course_fields = ("seed", "pool", "profile", "policy", "score", "dnf", "dnf_turn",
        "final_reserve", "spent", "reserve_remaining", "form_adjustment", "reserve_floor_clamped")
    turn_fields = ("seed", "pool", "profile", "policy", "segment", "roll", "choice",
        "current_difficulty", "physiological_load", "cost", "terrain_extra_cost", "spent",
        "reserve_remaining", "available", "payable")
    with courses_path.open("w", newline="", encoding="utf-8") as cf, turns_path.open("w", newline="", encoding="utf-8") as tf:
        cw = csv.DictWriter(cf, fieldnames=course_fields, lineterminator="\n"); cw.writeheader()
        tw = csv.DictWriter(tf, fieldnames=turn_fields, lineterminator="\n"); tw.writeheader()
        for pool, policy_name, (profile_name, profile) in product(POOLS_R1B2, POLICY_NAMES, profiles.items()):
            courses = []
            for seed in range(seeds):
                course = run_race(seed=seed, pool=pool, race_length=9, curve="B",
                    policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                    long_run_preparation=False, form_mode="PATTERN",
                    difficulty_profile=profile, profile_name=profile_name)
                courses.append(course)
                cw.writerow({field: course[field] for field in course_fields})
                for turn in course["turns"]:
                    row = {"seed": seed, "pool": pool.name, "profile": profile_name,
                           "policy": policy_name, **turn}
                    tw.writerow({field: json.dumps(row[field]) if isinstance(row[field], (tuple, list))
                                 else row[field] for field in turn_fields})
            grouped[(pool.name, profile_name, policy_name)] = courses
    return grouped


def validate_flat(grouped):
    checked = 0
    flat_names = {key[1] for key in grouped if grouped[key][0]["difficulty_profile"] == FLAT}
    for (pool_name, profile_name, policy_name), courses in grouped.items():
        if profile_name not in flat_names:
            continue
        for flat in courses:
            baseline = run_race(seed=flat["seed"], pool=POOLS[pool_name], race_length=9,
                curve="B", policy=POLICIES[policy_name], ctl=CTL_LEVEL, freshness_bonus=0,
                long_run_preparation=False, form_mode="PATTERN")
            for field in ("rolls", "signals", "form_adjustment", "final_reserve", "spent",
                          "reserve_remaining", "score", "dnf", "dnf_turn", "reserve_floor_clamped"):
                if flat[field] != baseline[field]:
                    raise RuntimeError(f"R1-B2 flat divergence: {pool_name}/{policy_name}/{flat['seed']}/{field}")
            if [turn["choice"] for turn in flat["turns"]] != [turn["choice"] for turn in baseline["turns"]]:
                raise RuntimeError(f"R1-B2 flat choice divergence: {pool_name}/{policy_name}/{flat['seed']}")
            checked += 1
    return checked


def validate_committed_r1b_flat(rows):
    with (RESULTS / "summary_r1b.csv").open(encoding="utf-8") as handle:
        baseline_rows = list(csv.DictReader(handle))
    expected = {(row["pool"], row["policy"]): row for row in baseline_rows
                if row["length"] == "9" and row["profile"] == "D0_FLAT"}
    checked = 0
    for row in rows:
        if row["difficulty_sum"] != 0:
            continue
        old = expected[(row["pool"], row["policy"])]
        for new_field, old_field in (("mean_score", "mean_score"), ("dnf_rate", "dnf_rate"),
                                     ("mean_spent", "mean_spent"),
                                     ("mean_reserve_remaining", "mean_reserve_remaining")):
            if abs(float(row[new_field]) - float(old[old_field])) > 1e-12:
                raise RuntimeError(f"committed R1-B flat divergence: {row['pool']}/{row['policy']}/{new_field}")
        checked += 1
    return checked


def profile_facts(profile):
    return {"difficulty_sum": sum(profile), "difficult_segments": sum(d > 0 for d in profile),
            "max_difficulty": max(profile)}


def course_metrics(course):
    turns = course["turns"]
    difficult = [turn for turn in turns if turn["current_difficulty"] > 0]
    plausible = [plausible_production_count(turn["payable"], "B", PRIMARY_PLAUSIBLE_MARGIN,
                                            turn["current_difficulty"]) for turn in turns]
    plausible_difficult = [plausible[i] for i, turn in enumerate(turns) if turn["current_difficulty"] > 0]
    productions = [turn["choice"] for turn in turns]
    return {
        "mean_production": statistics.mean(productions),
        "mean_p_difficult": statistics.mean(turn["choice"] for turn in difficult) if difficult else float("nan"),
        "terrain_extra_cost": sum(turn["terrain_extra_cost"] for turn in turns),
        "mean_plausible": statistics.mean(plausible),
        "mean_plausible_difficult": statistics.mean(plausible_difficult) if plausible_difficult else float("nan"),
        "forced_like": statistics.mean(value <= 1 for value in plausible),
        "forced_like_difficult": statistics.mean(value <= 1 for value in plausible_difficult) if plausible_difficult else float("nan"),
        "final_acceleration": len(productions) >= 3 and statistics.mean(productions[-2:]) > statistics.mean(productions[:-2]),
    }


def safe_mean(values):
    usable = [value for value in values if value == value]
    return statistics.mean(usable) if usable else ""


def paired_metrics(flat, terrain, profile):
    difficult_indices = [i for i, value in enumerate(profile) if value > 0]
    shared = [i for i in difficult_indices if i < len(flat["turns"]) and i < len(terrain["turns"])]
    deltas = [terrain["turns"][i]["choice"] - flat["turns"][i]["choice"] for i in shared]
    post_indices = [i for i in range(1, len(profile)) if profile[i] == 0 and profile[i - 1] > 0]
    post_p = [terrain["turns"][i]["choice"] - flat["turns"][i]["choice"] for i in post_indices
              if i < len(flat["turns"]) and i < len(terrain["turns"])]
    post_r = [terrain["turns"][i]["reserve_remaining"] - flat["turns"][i]["reserve_remaining"]
              for i in post_indices if i < len(flat["turns"]) and i < len(terrain["turns"])]
    return {"deltas": deltas, "post_p": post_p, "post_r": post_r}


def aggregate_rows(grouped, profiles, family, selected_magnitude=""):
    rows, paired_rows = [], []
    flat_name = next(name for name, profile in profiles.items() if profile == FLAT)
    for pool in POOLS_R1B2:
        for profile_name, profile in profiles.items():
            for policy_name in POLICY_NAMES:
                courses = grouped[(pool.name, profile_name, policy_name)]
                metrics = [course_metrics(course) for course in courses]
                flat = grouped[(pool.name, flat_name, policy_name)]
                facts = profile_facts(profile)
                all_deltas, all_post_p, all_post_r = [], [], []
                if profile != FLAT:
                    for baseline, terrain in zip(flat, courses):
                        paired = paired_metrics(baseline, terrain, profile)
                        all_deltas.extend(paired["deltas"]); all_post_p.extend(paired["post_p"]); all_post_r.extend(paired["post_r"])
                remaining = [course["reserve_remaining"] for course in courses if course["reserve_remaining"] is not None]
                turn_p = [safe_mean(course["turns"][i]["choice"] for course in courses if i < len(course["turns"])) for i in range(9)]
                turn_r = [safe_mean(course["turns"][i]["reserve_remaining"] for course in courses
                                    if i < len(course["turns"]) and course["turns"][i]["reserve_remaining"] is not None) for i in range(9)]
                row = {
                    "family": family, "pool": pool.name, "profile": profile_name,
                    "magnitude": facts["max_difficulty"] if profile != FLAT else 0,
                    "frequency": facts["difficult_segments"], "policy": policy_name,
                    "seeds": len(courses), **facts,
                    "mean_score": statistics.mean(c["score"] for c in courses),
                    "median_score": statistics.median(c["score"] for c in courses),
                    "dnf_rate": statistics.mean(c["dnf"] for c in courses),
                    "mean_spent": statistics.mean(c["spent"] for c in courses),
                    "mean_reserve_remaining": statistics.mean(remaining),
                    "mean_production": statistics.mean(m["mean_production"] for m in metrics),
                    "mean_p_difficult": safe_mean(m["mean_p_difficult"] for m in metrics),
                    "mean_delta_p_vs_flat": statistics.mean(all_deltas) if all_deltas else "",
                    "median_delta_p_vs_flat": statistics.median(all_deltas) if all_deltas else "",
                    "delta_p_distribution": json.dumps(dict(sorted(Counter(all_deltas).items()))) if all_deltas else "{}",
                    "mean_terrain_extra_cost": statistics.mean(m["terrain_extra_cost"] for m in metrics),
                    "mean_plausible_production_count": statistics.mean(m["mean_plausible"] for m in metrics),
                    "mean_plausible_difficult": safe_mean(m["mean_plausible_difficult"] for m in metrics),
                    "forced_like_rate": statistics.mean(m["forced_like"] for m in metrics),
                    "forced_like_difficult_rate": safe_mean(m["forced_like_difficult"] for m in metrics),
                    "slow_rate": sum(delta < 0 for delta in all_deltas) / len(all_deltas) if all_deltas else "",
                    "maintain_rate": sum(delta == 0 for delta in all_deltas) / len(all_deltas) if all_deltas else "",
                    "attack_rate": sum(delta > 0 for delta in all_deltas) / len(all_deltas) if all_deltas else "",
                    "mean_post_difficulty_delta_p": statistics.mean(all_post_p) if all_post_p else "",
                    "mean_post_difficulty_delta_reserve": statistics.mean(all_post_r) if all_post_r else "",
                    "final_acceleration_rate": statistics.mean(m["final_acceleration"] for m in metrics),
                    "turn_mean_production": json.dumps(turn_p), "turn_mean_reserve_remaining": json.dumps(turn_r),
                }
                rows.append(row)
                if profile != FLAT:
                    paired_rows.append({key: row[key] for key in (
                        "family", "pool", "profile", "magnitude", "frequency", "policy", "seeds",
                        "mean_delta_p_vs_flat", "median_delta_p_vs_flat", "delta_p_distribution",
                        "slow_rate", "maintain_rate", "attack_rate", "mean_post_difficulty_delta_p",
                        "mean_post_difficulty_delta_reserve", "mean_terrain_extra_cost",
                        "mean_plausible_difficult", "forced_like_difficult_rate")})
    return rows, paired_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("magnitude", "remaining"), required=True)
    parser.add_argument("--selected-magnitudes", nargs=2, type=int, default=(2, 3))
    parser.add_argument("--seeds", type=int, default=500)
    parser.add_argument("--output", type=Path, default=RESULTS)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    all_paired = []
    if args.phase == "magnitude":
        grouped = simulate(MAGNITUDE_PROFILES, args.seeds, "magnitude", args.output)
        flat_checked = validate_flat(grouped)
        rows, paired = aggregate_rows(grouped, MAGNITUDE_PROFILES, "MAGNITUDE")
        committed_flat_checked = validate_committed_r1b_flat(rows)
        write_csv(args.output / "summary_r1b2_magnitude.csv", rows)
        all_paired.extend(paired)
        configurations = len(grouped)
        executed_configurations = configurations
        courses = configurations * args.seeds
    else:
        frequency = frequency_profiles(args.selected_magnitudes)
        frequency_grouped = simulate(frequency, args.seeds, "frequency", args.output)
        flat_checked = validate_flat(frequency_grouped)
        frequency_rows, frequency_paired = aggregate_rows(frequency_grouped, frequency, "FREQUENCY")
        committed_flat_checked = validate_committed_r1b_flat(frequency_rows)
        write_csv(args.output / "summary_r1b2_frequency.csv", frequency_rows)
        nonflat_profiles = {name: profile for name, profile in REPRESENTATIVE_PROFILES.items() if profile != FLAT}
        profile_grouped = simulate(nonflat_profiles, args.seeds, "profiles", args.output)
        # P0 is exactly F0: reuse the already simulated courses, not just their summary.
        for pool in POOLS_R1B2:
            for policy_name in POLICY_NAMES:
                profile_grouped[(pool.name, "P0", policy_name)] = frequency_grouped[(pool.name, "F0", policy_name)]
        flat_checked += validate_flat(profile_grouped)
        profile_rows, profile_paired = aggregate_rows(profile_grouped, REPRESENTATIVE_PROFILES, "PROFILES")
        write_csv(args.output / "summary_r1b2_profiles.csv", profile_rows)
        all_paired.extend(frequency_paired + profile_paired)
        configurations = len(frequency_grouped) + len(profile_grouped)
        executed_configurations = len(frequency_grouped) + len(nonflat_profiles) * len(POOLS_R1B2) * len(POLICY_NAMES)
        courses = executed_configurations * args.seeds
    paired_path = args.output / f"paired_terrain_effects_{args.phase}.csv"
    if args.phase == "remaining":
        magnitude_path = args.output / "paired_terrain_effects_magnitude.csv"
        if not magnitude_path.exists():
            raise RuntimeError("magnitude phase outputs are required before remaining phase")
        with magnitude_path.open(encoding="utf-8") as handle:
            all_paired = list(csv.DictReader(handle)) + all_paired
        paired_path = args.output / "paired_terrain_effects.csv"
    write_csv(paired_path, all_paired)
    metadata_path = args.output / f"run_metadata_r1b2_{args.phase}.json"
    metadata = {
        "experiment": "EXP R1-B2 DIFFICULTY MAGNITUDE x FREQUENCY", "status": "EXPERIMENTAL ONLY",
        "phase": args.phase, "seeds": args.seeds, "seed_range": f"0..{args.seeds - 1}",
        "configuration_count": configurations, "course_count": courses, "length": 9,
        "executed_configuration_count": executed_configurations,
        "form_mode": "PATTERN", "curve": "B", "sl": False, "freshness": 0, "ctl": CTL_LEVEL,
        "pools": [pool.name for pool in POOLS_R1B2], "policies": list(POLICY_NAMES),
        "selected_magnitudes": list(args.selected_magnitudes) if args.phase == "remaining" else None,
        "flat_baseline_courses_checked": flat_checked, "runtime_seconds": time.perf_counter() - started,
        "committed_r1b_flat_summary_rows_checked": committed_flat_checked,
        "plausible_efficiency_margin": PRIMARY_PLAUSIBLE_MARGIN,
        "strict_choice_labels": "SLOW delta<0; MAINTAIN delta=0; ATTACK delta>0",
        "baseline_git_head_at_run": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
            text=True, capture_output=True, check=True).stdout.strip(),
        "large_ignored_outputs": (["courses_r1b2_frequency.csv", "turns_r1b2_frequency.csv",
                                   "courses_r1b2_profiles.csv", "turns_r1b2_profiles.csv"]
                                  if args.phase == "remaining" else
                                  ["courses_r1b2_magnitude.csv", "turns_r1b2_magnitude.csv"]),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    if args.phase == "remaining":
        magnitude_metadata_path = args.output / "run_metadata_r1b2_magnitude.json"
        magnitude_metadata = json.loads(magnitude_metadata_path.read_text())
        combined = {
            "experiment": metadata["experiment"], "status": metadata["status"],
            "phases": {"magnitude": magnitude_metadata, "frequency_and_profiles": metadata},
            "total_course_executions": magnitude_metadata["course_count"] + metadata["course_count"],
            "technical_magnitude_selection": {
                "selected": list(args.selected_magnitudes),
                "rationale": "D2 and D3 preserved distinct policy responses and non-myopic DNF while D1 was milder and D4 caused material ADAPTIVE DNF.",
            },
        }
        (args.output / "run_metadata_r1b2.json").write_text(json.dumps(combined, indent=2) + "\n")
        magnitude_path.unlink()
        magnitude_metadata_path.unlink()
        metadata_path.unlink()
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
