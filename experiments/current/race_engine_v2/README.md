# EXP R1-A — Race Engine V2 / flat terrain

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.** This isolated harness neither
replaces `race_core` nor changes training, Fatigue V1, CTL thresholds, or the GDD.

## Boundaries

`core.py` owns legal resolution and never selects a Production. `policies.py`
contains deterministic technical probes. `run.py` defines the campaigns and
aggregation. A segment rolls the full supplied pool, classifies form from that
raw roll during segments 1–3, exhaustively enumerates every non-empty subset,
deduplicates sums, and then asks the policy to choose from the payable sums.
Rolls are pre-generated from a private seeded RNG, so policy choices cannot
change later rolls.

Segments 1–3 cannot be cancelled retroactively. S3 reveals the raw final
reserve; after its choice, `max(raw final reserve, Spent_3)` applies the required
floor and records a clamp. From segment 4 onward, a sum is legal only when its
cost fits remaining reserve; no payable non-empty sum means DNF.

## Frozen experimental fixtures

Energy tables are inclusive upper bounds; the final value applies at 27+:

| Curve | ≤15 | 16–18 | 19–21 | 22 | 23 | 24 | 25 | 26 | ≥27 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 1 | 2 | 2 | 3 | 4 | 5 | 7 | 9 | 12 |
| B | 1 | 2 | 2 | 3 | 5 | 7 | 10 | 13 | 16 |
| C | 1 | 2 | 3 | 5 | 8 | 12 | 16 | 20 | 25 |

A/C are arbitrary `EXPERIMENTAL FIXTURE`s. The CTL fixture is
`2 × race_length + floor(CTL/50)`, with CTL fixed at 100. Freshness is supplied
directly as 0 or +3. Form uses exact full-roll-sum distributions per pool and
the first attainable cumulative thresholds at 20%, 70%, and 93%; the resulting
classes map to -1/0/+1/+2. SL changes LOW only, from -1 to 0. These conventions
are reproducible technical choices, not validated design.

Pools include the required `6d6`, `4d8+1d6`, and `2d10+4d6`. Two progression-
reachable fixtures are added from `dice_progression.py`: `1d8+3d6` after one
upgrade, and `1d12+1d8+4d6` at CTL 100 after four concentrated upgrades.
The two required mixed priority pools are explicit comparison fixtures; this
harness does not claim that every required composition is produced by the
current automatic upgrade policy.

## Reproduction

```bash
python -m unittest experiments.current.race_engine_v2.test_harness -v
python experiments/current/race_engine_v2/run.py --phase smoke
python experiments/current/race_engine_v2/run.py --phase all
```

`all` runs the exact 50-seed smoke first and stops if policies fail to diverge,
then targeted 500-seed contrasts: curve/pool (neutral preparation), SL on versus
the neutral Curve-B baseline, and freshness +3 versus that baseline. Compact
`summary.csv`, `pattern_stats.csv`, `granularity_stats.json`, and
`run_metadata.json` are versioned. Reproducible `courses.csv` and `turns.csv`
are generated under `results/` but ignored because they are large.

## R1-A2 — Form pattern normalization

R1-A2 adds a `form_mode="SUM" | "PATTERN"` switch without duplicating or
recalibrating the race engine. `SUM` is the unchanged R1-A baseline. `PATTERN`
uses only multiplicities, repeated groups, full/four-kind flags, longest run,
and distinct-value count; it never uses raw-roll sum or selected Production.
Its compact score is normalized against the exact outcome distribution of each
pool. See `REPORT_R1A2.md` for the controlled Curve-B comparison.

```bash
python -m unittest experiments.current.race_engine_v2.test_r1a2 -v
python experiments/current/race_engine_v2/run_r1a2.py --seeds 10 --output /tmp/r1a2-smoke
python experiments/current/race_engine_v2/run_r1a2.py --seeds 500
```

## R1-B — Local difficulty

R1-B keeps FORM_PATTERN and Curve B as experimental technical baselines. A
public per-segment difficulty changes only physiological load:
`load = Production + difficulty`, then `cost = CurveB(load)`. Score remains the
chosen Production. Terrain has no persistent state; only spent reserve carries
its consequence forward.

```bash
python -m unittest experiments.current.race_engine_v2.test_r1b -v
python experiments/current/race_engine_v2/run_r1b.py --phase smoke --output /tmp/r1b-smoke
python experiments/current/race_engine_v2/run_r1b.py --phase main
```

See `REPORT_R1B.md`. Detailed course/turn CSVs are reproducible and ignored;
only compact R1-B summaries, paired comparisons, and metadata are versioned.

## R1-B2 — Difficulty magnitude × frequency

R1-B2 changes no engine rule or policy. It calibrates the already implemented
local difficulty with 9-segment, paired-seed sweeps: magnitude 1–4 at fixed
placement, frequency 2/3/4 for the technically central magnitudes 2 and 3, and
the P1/P2/P3 representative profiles. Run the phases in order:

```bash
python experiments/current/race_engine_v2/run_r1b2.py --phase magnitude
python experiments/current/race_engine_v2/run_r1b2.py --phase remaining --selected-magnitudes 2 3
```

See `REPORT_R1B2.md`. Large phase-level course/turn CSVs are ignored.
