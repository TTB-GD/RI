# Training V2 → Race V2 minimal bridge


> **EXPERIMENTAL SPEC PROBE — SPEC IS OPEN / NOT IMPLEMENTED.** This is not
> the integrated V2 baseline. SPEC is
> OPEN and not implemented in the active Race V2 path; Position, Efficacité and
> AS42/AS21/AS10/AS5 below are preserved experimental conventions only.

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN**

This isolated probe connects synthetic Training V2 SPEC allocations to the
existing experimental Race Engine V2 primitives. It changes neither production
code nor CURRENT tests, and it does not simulate training longitudinally.

## Scope and fixed fixtures

- Two contexts only: AS42 starts at 17 (`15 EF < 17 < 21 Seuil`) and AS10 at
  22 (`21 Seuil < 22 < 27 VMA`). These are probe parameters, not design values.
- One shared physiology (EF 15, Seuil 21, VMA 27), `6d6` pool, Curve B, six
  flat segments, CTL 100, freshness 0, and FORM_PATTERN.
- 20 shared seeds × 2 contexts × 3 builds = 120 courses.
- Four SPEC tiers per build: SPEED 4/0, BALANCED 2/2, ECONOMY 0/4
  (POSITION/EFFICIENCY). Impossible tiers are reported, never converted.
- `ECO_MAX = min(C0(AS)-C0(EF), C0(VMA)-C0(AS))`; effective ECO is capped by
  that envelope and applies at the exact active AS only. The cost floor is C0(EF).

## Reuse and experimental adapter

The harness imports the unchanged Race Engine V2 dice generation, persistent
pool fixture, subset enumeration, form classification, reserve mapping and
Curve B cost function. Since its normative runner has no cost-adapter hook, the
local runner preserves its segment order and reserve-finalization rule while
injecting effective cost only at exact AS.

`SPEC_TARGET_SUSTAINABLE` is the sole experimental policy. It selects the
highest rolled subset Production at or below active AS that leaves one EF-cost
unit per future segment; if none is sustainable it selects the cheapest payable
option. It contains no build label or bonus. Ties are deterministic. POSITION
changes only its AS target; it does not change pool, roll, reserve, freshness or
difficulty.

Run:

```bash
python -m experiments.current.training_race_bridge.harness
python -m unittest experiments.current.training_race_bridge.test_harness -v
```

`results.json` contains protocol, synthetic athletes, aggregate metrics, all
required seed-paired differences, and per-course traces.


## Training B → Race V2 — direct integration

The files `training_b_adapter.py`, `training_b_race_harness.py` and
`test_training_b_adapter.py` add a separate direct integration path from the
actual `training_v2.PlayerState` / completed Training B trajectory snapshot.

- EF, Seuil and VMA are copied one-to-one into Race V2's
  `PhysiologyProfile`; no hidden scale conversion is applied.
- The persistent Training B die sizes are copied one-to-one into Race V2's
  `DicePool`.
- A 16-turn Training B trajectory is then passed to Race V2 and resolved over
  six race segments. The harness runs three seeds across balanced, EF and
  quality training heuristics (nine paired preparation/race cases).
- CTL, freshness and long-run preparation remain explicit Race V2 inputs. The
  harness uses CTL 100, freshness 0 and no long-run preparation as declared
  experimental fixtures, not as Training B conversions.

Run:

```bash
python -m experiments.current.training_race_bridge.training_b_race_harness
python -m unittest experiments.current.training_race_bridge.test_training_b_adapter -v
```

**Calibration gap:** Training B's initial profile is EF 6 / Seuil 8 / VMA 10,
whereas prior Race V2 calibration probes commonly used EF 15 / Seuil 21 /
VMA 27. The adapter deliberately preserves the Training B values instead of
inventing a scale factor. Race completion and reserve adequacy must therefore
be evaluated before treating this vertical slice as balanced. The earlier
synthetic SPEC probe above remains separate and is not evidence of Training B
integration.


## Pool-expectation normalization — paired 20-seed probe

The direct Race V2 runner now exposes an **opt-in experimental** divisor for
physiological cost. The default divisor remains 1.0, so all existing Race V2
behaviour is unchanged. For the comparison, the normalized variant uses:

```
normalized_cost = physiological_cost / E(actual Training B dice pool)
```

The same 16-turn Training B trajectory, resulting profile, persistent pool,
race seed, policy and reserve fixture are used for raw and normalized runs.
The reserve formula remains unchanged at CTL 100 / six segments (14 points);
interpreting those 14 points in normalized units is still a calibration
hypothesis, not a confirmed CTL conversion.

CI run 42893031947 tested 20 seeds per focus (60 Training B preparations,
120 paired Race V2 executions). A follow-up run 42893537620 tested the same
60 preparations at CTL 100, 150 and 200, using the existing reserve formula:

| Training focus | Raw CTL100 | Normalized CTL100 | Normalized CTL150 | Normalized CTL200 |
|---|---:|---:|---:|---:|
| Balanced | 0/20 | 14/20 (70%) | 19/20 (95%) | 20/20 (100%) |
| EF | 0/20 | 15/20 (75%) | 18/20 (90%) | 19/20 (95%) |
| Quality | 0/20 | 18/20 (90%) | 20/20 (100%) | 20/20 (100%) |
| **Total** | **0/60** | **47/60 (78.3%)** | **57/60 (95%)** | **59/60 (98.3%)** |

The normalized DNF cases all occur on segment 6. The reserve formula adds one
point when CTL rises from 100 to 150 and another at 200. This sensitivity result
shows that the remaining failures are strongly related to reserve magnitude;
it does **not** establish that Training B should produce CTL 150 or 200, nor
that this reserve mapping is correctly dimensioned.

The exact-division candidate retains fractional costs. A separate integer-
ceiling candidate is recorded in PR50 and produced 4/9 finishes on its initial
three-seed sample. These two quantization approaches should not be treated as
equivalent.

Run:

```bash
python -m unittest experiments.current.training_race_bridge.test_training_b_adapter -v
```


## Persistent pool progression at fixed physiology

A separate probe holds the same Training B physiology profile fixed (the
balanced seed-11, 16-turn profile) and varies only the persistent dice pool.
Each pool is normalized by its own expectation; 20 race seeds are used per
pool, with CTL 100, six flat segments and ADAPTIVE policy.

| Pool | E(pool) | Variance | Finish | Mean score | Mean spend |
|---|---:|---:|---:|---:|---:|
| 4d6 | 14.0 | 11.67 | 3/20 (15%) | 50.40 | 13.164 |
| 4d8 | 18.0 | 21.00 | 17/20 (85%) | 77.60 | 12.350 |
| 4d8+1d6 | 21.5 | 23.92 | 20/20 (100%) | 96.75 | 10.605 |
| 2d10+4d6 | 25.0 | 28.17 | 20/20 (100%) | 117.15 | 9.120 |

CI run 42893866549 passed 138 primary tests and 88 lightweight experimental
tests. The progression probe shows a clear pool-size benefit in this fixture.
Expectation and variance both rise across these pools, so this does not yet
separate their individual contributions; an equal-expectation/different-
variance comparison remains open.


## Equal-expectation / different-variance comparison

To separate expectation from variance, the same fixed physiology profile is
tested against pairs of pools with equal E(pool) but different face
composition and variance. Each pool runs 20 seeds, normalized by the shared
expectation, at CTL 100.

| Equal E(pool) | Pool | Variance | Finish | Mean score |
|---:|---|---:|---:|---:|
| 18.0 | 4d8 | 21.00 | 17/20 (85%) | 77.60 |
| 18.0 | 2d6+2d10 | 22.33 | 20/20 (100%) | 83.35 |
| 22.5 | 5d8 | 26.25 | 20/20 (100%) | 103.00 |
| 22.5 | 3d6+1d10+1d12 | 28.92 | 20/20 (100%) | 103.70 |
| 27.0 | 6d8 | 31.50 | 20/20 (100%) | 126.70 |
| 27.0 | 3d6+3d10 | 33.50 | 20/20 (100%) | 126.85 |

At E(pool)=18, the higher-variance pool improves completion from 85% to 100%.
At the two higher expectations, all pools finish and score differences are
small. This indicates variance can matter near the viability boundary, but
does not establish a general variance bonus. CI run 42894254229 passed 138
primary and 89 experimental tests.


## Second Training B profile and terrain check

The equal-expectation pairs were repeated on a second 16-turn Training B
profile (EF-focused, seed 23), with flat course and an early-hills profile
(+3 load on segments 2–3). Twenty seeds per pool:

| E(pool) | Pool | Finish flat / hills | Mean score | Mean max load flat → hills | Mean terrain surcharge |
|---:|---|---:|---:|---:|---:|
| 18.0 | 4d8 | 0% / 0% | 60.20 | 13.85 → 16.35 | 0.000 |
| 18.0 | 2d6+2d10 | 15% / 15% | 67.50 | 14.25 → 17.10 | 0.000 |
| 22.5 | 5d8 | 70% / 70% | 95.10 | 18.45 → 20.35 | 0.000 |
| 22.5 | 3d6+1d10+1d12 | 65% / 65% | 94.50 | 18.55 → 20.45 | 0.000 |
| 27.0 | 6d8 | 100% / 100% | 124.10 | 23.70 → 24.40 | 0.000 |
| 27.0 | 3d6+3d10 | 100% / 100% | 124.65 | 23.55 → 24.40 | 0.000 |

The +3 terrain load is present, but the physiological surcharge remains zero in
all cases. This is consistent with the selected loads remaining below the EF
cost floor: the current cost function therefore does not activate its
threshold/VMA slopes in this test. This is an important remaining integration
gap, not evidence that terrain has no game effect in every configuration.
CI run 42894769395 passed 138 primary and 90 experimental tests.


## Physiological landmark activation check

The 20-seed end-to-end matrix now counts both selected race loads and every
legal production option against EF / Seuil / VMA (normalized cost, CTL 100):

| Training focus | Selected loads ≤ EF | Legal options ≤ EF | Legal options EF–Seuil | Legal options > Seuil |
|---|---:|---:|---:|---:|
| Balanced | 114/114 | 1,865 | 0 | 0 |
| EF | 115/115 | 1,976 | 0 | 0 |
| Quality | 118/118 | 1,766 | 2 | 0 |

Thus the policy-selected loads never leave the EF floor. Even across all legal
options, only 2 of 1,768 quality-focus options exceed EF; none reaches the
Seuil–VMA zone. The threshold and VMA cost slopes are effectively dormant in
these end-to-end fixtures. This confirms a profile/load-scale integration gap:
pool normalization alone does not make Training B's physiological landmarks
mechanically active in Race V2.
