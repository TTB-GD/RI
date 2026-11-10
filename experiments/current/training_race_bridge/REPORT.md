# Training V2 → Race V2 minimal bridge — report

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN**

## FACT

- The adapter calls Race Engine V2's existing seeded rolls, persistent `6d6`
  pool, subset Production enumeration, FORM_PATTERN classification, CTL reserve
  mapping, and Curve B. No production or CURRENT file was changed.
- All builds share EF 15, Seuil 21, VMA 27, pool, reserve, freshness and rolls.
  Their only input difference is four SPEC tiers split 4/0, 2/2 or 0/4.
- Curve B gives C0(EF=15)=1 and C0(VMA=27)=16. Exact-AS ECO uses the specified
  envelope and can never reduce a cost below 1.
- No POSITION tier is unusable in these fixtures. Effective ECO is respectively
  0/1/1 for SPEED/BALANCED/ECONOMY in AS42 and 0/2/2 in AS10; capped EFFICIENCY
  tiers are explicitly recorded as unusable rather than converted.

## PROTOCOL

Twenty shared seeds (0–19), two contexts, three builds, one six-segment flat
race and one policy produced **120 courses**, below the 180-course ceiling.
AS42 starts at 17 and AS10 at 22; POSITION moves their active AS upward by one
Production per usable tier. These are probe fixtures, not proposed design values.

`SPEC_TARGET_SUSTAINABLE` takes the highest rolled subset at or below active AS
while preserving one EF-cost per remaining segment. If impossible, it takes the
cheapest payable subset. It knows neither build name nor an abstract POSITION
bonus. Runs within each context/seed use identical pre-generated rolls; policy
choices do not consume RNG, so pairing is exact for rolls, pool and form.

## RESULTS

Means over 20 courses per row (P/cost is descriptive, not an official score):

| Context | Build | Finish | Production | P/segment | Cost | Reserve left | AS segments | Cost at AS | ECO triggers | P/cost | At / below / above AS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AS42 | SPEED | 100% | 114.40 | 19.07 | 11.25 | 3.50 | 2.45 | 4.90 | 0.00 | 10.18 | 40.8% / 59.2% / 0% |
| AS42 | BALANCED | 100% | 107.60 | 17.93 | 7.55 | 7.20 | 3.70 | 3.70 | 3.70 | 14.55 | 61.7% / 38.3% / 0% |
| AS42 | ECONOMY | 100% | 98.75 | 16.46 | 6.65 | 8.10 | 4.60 | 4.60 | 4.60 | 15.13 | 76.7% / 23.3% / 0% |
| AS10 | SPEED | 100% | 112.15 | 18.69 | 14.15 | 0.60 | 0.00 | 0.00 | 0.00 | 7.98 | 0% / 100% / 0% |
| AS10 | BALANCED | 100% | 114.50 | 19.08 | 14.15 | 0.60 | 0.85 | 4.25 | 0.85 | 8.15 | 14.2% / 85.8% / 0% |
| AS10 | ECONOMY | 100% | 117.10 | 19.52 | 9.35 | 5.40 | 1.90 | 1.90 | 1.90 | 12.88 | 31.7% / 68.3% / 0% |

Reserve first constrained a choice in 18/20 AS10 SPEED courses (mean first
segment 3.67) and 16/20 BALANCED courses (4.81), but in no AS42 or AS10 ECONOMY
course. This metric excludes mere absence of exact AS from a roll.

## PAIRED DIFFERENCES

Mean seed-paired deltas; `n≠0` reports how many of 20 pairs differ in the four
metrics, showing that averages do not hide universal convergence.

| Context | Pair | Δ Production | Δ Cost | Δ reserve | Δ AS segments | n≠0 (P/cost/reserve/AS) |
|---|---|---:|---:|---:|---:|---:|
| AS42 | SPEED − BALANCED | +6.80 | +3.70 | −3.70 | −1.25 | 20/20/20/17 |
| AS42 | SPEED − ECONOMY | +15.65 | +4.60 | −4.60 | −2.15 | 20/20/20/20 |
| AS42 | BALANCED − ECONOMY | +8.85 | +0.90 | −0.90 | −0.90 | 20/15/15/15 |
| AS10 | SPEED − BALANCED | −2.35 | 0.00 | 0.00 | −0.85 | 13/0/0/13 |
| AS10 | SPEED − ECONOMY | −4.95 | +4.80 | −4.80 | −1.90 | 14/19/19/18 |
| AS10 | BALANCED − ECONOMY | −2.60 | +4.80 | −4.80 | −1.05 | 16/19/19/18 |

Every individual paired delta is retained in `results.json`.

## OBSERVATIONS

1. **Q1/Q5 — yes:** profiles differ on Production, cost, AS usage and reserve in
   both contexts. AS42 gives an ordered Production/cost trade-off. AS10 gives a
   different ordering because reserve constrains the higher targets.
2. **Q2 — context-dependent:** SPEED produces most in AS42 and pays most, but
   its AS10 target (26, cost 13) is never selected sustainably. It therefore
   produces less than the lower-AS builds there. POSITION changes decisions,
   but not always by enabling its active AS.
3. **Q3 — yes in this policy/fixture:** ECONOMY repeats exact AS most and retains
   most reserve in both contexts; ECO triggers 4.60 and 1.90 times per course.
4. **Q4 — only in AS42:** BALANCED is numerically intermediate there. In AS10 it
   shares SPEED's mean cost/reserve, while its Production and AS use lie between
   SPEED and ECONOMY. “Intermediate” is metric- and context-dependent.
5. **Q6:** AS/ECO is visible. Curve B and finite reserve amplify it in AS10:
   Curve B makes SPEED's exact AS too expensive for this sustainability policy.
   Pool subset availability also limits exact-AS frequency.

## INTERPRETATIONS

The stop criterion is met: equal SPEC budgets create clearly distinct course
profiles without changing Race Engine V2. This supports returning the mechanical
bridge to Game Design review; it does **not** establish balance or player behavior.
The AS10 reversal is especially informative: more POSITION creates theoretical
Production headroom, while Curve B plus reserve prevents this policy from using
it. That is an interaction result, not evidence that any build is “better.”

## LIMITS

- Synthetic states bypass all longitudinal Training V2 outcomes.
- The sole policy is an experimental deterministic convention, not a normative
  player model. Its ceiling at AS deliberately yields no above-AS selections.
- Only Curve B, flat difficulty, `6d6`, six segments, CTL 100 and 20 seeds are
  covered. No balancing conclusion generalizes beyond this probe.
- Race Engine V2 currently exposes no custom-cost hook, so the local adapter
  reproduces its relevant loop rather than calling `run_race`; targeted tests
  and shared imported primitives bound, but cannot eliminate, drift risk.
- Form can change final reserve but paired rolls make that effect common within
  each context/seed. Courses remain policy counterfactuals, not human choices.

## DESIGN QUESTIONS

1. Should a high active AS that is mechanically reachable but unsustainable
   under Curve B be considered useful POSITION headroom or a failed SPEC option?
2. Is “BALANCED” expected to be intermediate on every metric, or only to expose
   a mixed set of options whose value remains context-dependent?
3. Should future policy work permit deliberate above-AS Production, given that
   this minimal policy isolates at/below-AS choices only?


## Direct Training B integration (new adapter)

The direct adapter now converts a completed Training B state into Race V2
inputs and executes the existing Race V2 runner. The integration harness
covers nine cases: three 16-turn Training B focus heuristics (balanced, EF,
quality) across seeds 11, 23 and 47, each followed by a six-segment Race V2
course using the same seed and ADAPTIVE technical policy.

The adapter copies EF/Seuil/VMA and every persistent die size without
rescaling. CTL=100, freshness=0 and no long-run preparation are explicit
experimental Race V2 fixtures; they are not inferred from Training B.

**Known calibration gap:** Training B starts at EF 6 / Seuil 8 / VMA 10,
while the earlier Race V2 calibration fixtures used EF 15 / Seuil 21 / VMA 27.
A direct structural conversion is implemented, but no approved numerical
cross-calibration exists. Consequently, these nine runs validate the software
connection and expose course completion/reserve behaviour; they do not
validate balance or prove that Training B currently produces viable race
profiles. The older synthetic SPEC results above must not be attributed to
Training B.


## First end-to-end observation (CI run, 9 paired cases)

The direct Training B trajectory harness was executed by the CI test suite:
three 16-turn preparation heuristics × seeds 11, 23 and 47, followed by six
Race V2 segments. All nine software paths execute, but **none of the nine
courses finishes** under the explicitly fixed CTL 100 / freshness 0 / SL off
inputs and ADAPTIVE policy.

| Training focus | Mean race score | Mean spent | Finish rate | Race pool |
|---|---:|---:|---:|---|
| Balanced | 44.00 | 129.00 | 0% | 4d8+1d6 |
| EF | 44.00 | 139.00 | 0% | 4d8+1d6 |
| Quality | 40.67 | 81.00 | 0% | 4d8 or 4d8+1d6 |

Observed final profile ranges across the three seeds:
- Balanced: EF 38–47, Seuil 48–56, VMA 49–57.
- EF: EF 44–49, Seuil 45–50, VMA 46–52.
- Quality: EF 26–29, Seuil 51–63, VMA 52–65.

**RESULT:** The software adapter is functional and preserves differentiated
Training B outputs, but the current Training B profile scale and Race V2
reserve/cost scale are not interoperable as a playable race. The result is not
a balance failure of the adapter; it is a concrete calibration/interface gap.
No conversion factor or reserve multiplier has been introduced.

**Next implementation gate:** determine how Training B physiological values
map to Race V2's cost domain and how the race reserve is funded. These two
rules must be made coherent together; tuning only one in isolation would hide
the dimensional mismatch. The direct adapter remains an experimental bridge
until this is resolved.


## Pool-expectation normalization — paired 20-seed validation

### RULE UNDER TEST

The experimental runner accepts an explicit `physiology_cost_divisor`.
With the divisor set to the expectation of the actual persistent Training B
pool, it charges:

[
C_{pool} = C_{physio} / E(P)
]

This probe uses exact division (fractional resource costs), not integer
rounding. The default divisor remains 1.0 and preserves the original Race V2
cost path. The reserve formula is unchanged: CTL 100 and six segments produce
14 reserve points. Treating those points as pool-normalized units remains an
explicit hypothesis.

### PROTOCOL

- 20 seeds (0–19) × three Training B focus heuristics = 60 preparations.
- Each completed preparation is run twice: raw physiological cost and cost
  divided by its actual pool expectation = 120 Race V2 executions.
- Both variants share the same Training B state, pool, race seed, ADAPTIVE
  policy, six-segment course, CTL 100, freshness 0 and SL off.
- CI runs: `42893031947` (20-seed paired cost comparison) and `42893537620` (reserve sensitivity); 87 tests passed in the latest run.

### RESULTS — COST NORMALIZATION AT CTL 100

| Training focus | Raw finish | Pool-normalized finish | Mean score | Mean spend | Mean E(pool) |
|---|---:|---:|---:|---:|---:|
| Balanced | 0/20 | 14/20 (70%) | 90.50 | 11.986 | 21.50 |
| EF | 0/20 | 15/20 (75%) | 93.75 | 12.523 | 22.02 |
| Quality | 0/20 | 18/20 (90%) | 90.55 | 10.049 | 20.45 |
| **Total** | **0/60** | **47/60 (78.3%)** | — | — | — |

All 13 normalized DNFs occur on segment 6. Raw-cost races all DNF on segment 4.

### RESERVE SENSITIVITY — SAME 60 TRAINING B PREPARATIONS

The same prepared profiles, persistent pools, seeds and ADAPTIVE policy were
rerun with the existing Race V2 CTL reserve formula at CTL 100, 150 and 200.
No reserve multiplier or new formula was introduced.

| Training focus | Normalized CTL100 | Normalized CTL150 | Normalized CTL200 |
|---|---:|---:|---:|
| Balanced | 14/20 (70%) | 19/20 (95%) | 20/20 (100%) |
| EF | 15/20 (75%) | 18/20 (90%) | 19/20 (95%) |
| Quality | 18/20 (90%) | 20/20 (100%) | 20/20 (100%) |
| **Total** | **47/60 (78.3%)** | **57/60 (95%)** | **59/60 (98.3%)** |

Every remaining normalized DNF is at segment 6. The existing reserve formula
adds one reserve point between CTL 100 and 150, then one more between 150 and
200. This indicates a reserve-magnitude sensitivity, but does not prove that
Training B should output CTL 150/200 or validate the CTL-to-reserve mapping.

### INTERPRETATION

- **RESULT:** Direct Training B → Race V2 integration remains structurally valid.
- **RESULT:** Dividing physiological cost by actual pool expectation changes the 0/60 raw finish rate to 47/60. It removes the systematic segment-4 DNF but does not make every profile viable.
- **RESULT:** The training focus remains observable. Quality has the highest finish rate (90%) and lowest mean spend; EF has the highest mean score. This does not establish a globally superior preparation strategy.
- **HYPOTHESIS:** Exact fractional pool-relative cost is a more promising interface than raw profile cost under the existing reserve fixture.
- **LIMIT:** This is still only 20 seeds per focus. The unchanged reserve of 14 has not been derived dimensionally from CTL in pool-relative units.

### ROUNDING COMPARISON

PR50 separately tested the integer-ceiling variant
`max(1, ceil(C_physio / E(P)))` on the original nine cases. It finished 4/9
(44.4%): balanced 1/3, EF 0/3, quality 3/3. That result is materially more
restrictive than exact division. It demonstrates that rounding is not a
cosmetic implementation detail; it changes the game outcome and must remain
an explicit open calibration choice.

### NEXT VALIDATION

1. Hold physiology fixed and compare multiple persistent pools to isolate
   whether higher expectation and variance improve race options without
   granting an unintended cost discount.
2. Isolate pool progression at fixed physiology to ensure the normalization
   neither erases nor double-counts the benefit of a stronger persistent pool.
3. Test course difficulty, then derive the CTL → reserve mapping in the same
   unit system before promoting either normalization rule.


## Persistent pool progression — physiology held constant

### PROTOCOL

A fixed Training B profile is taken from the balanced seed-11 trajectory after
16 turns. That exact EF / Seuil / VMA profile is held constant while the
persistent pool changes across four reachable/representative configurations.
Each pool is normalized by its own expectation. Twenty race seeds are run per
pool, with CTL 100, six flat segments, no freshness, no SL preparation and
the ADAPTIVE policy. Total: 80 Race V2 runs.

### RESULTS

| Pool | E(pool) | Variance | Finish rate | Mean score | Mean spend |
|---|---:|---:|---:|---:|---:|
| 4d6 | 14.0 | 11.67 | 3/20 (15%) | 50.40 | 13.164 |
| 4d8 | 18.0 | 21.00 | 17/20 (85%) | 77.60 | 12.350 |
| 4d8+1d6 | 21.5 | 23.92 | 20/20 (100%) | 96.75 | 10.605 |
| 2d10+4d6 | 25.0 | 28.17 | 20/20 (100%) | 117.15 | 9.120 |

### INTERPRETATION

- **RESULT:** With physiology fixed, larger/more capable pools materially
  improve production and race completion under the tested normalized-cost
  rule. The 4d6 pool finishes 3/20; 4d8 finishes 17/20; the two stronger pools
  finish 20/20.
- **RESULT:** The normalization does not erase the visible benefit of pool
  progression in this fixture.
- **LIMIT:** Expected total and variance both increase across the tested pools.
  This experiment therefore does not isolate the expectation effect from the
  variance / face-size effect, and only one physiological profile and policy
  are tested.
- **CI:** Run `42893866549` passed 138 primary tests and 88 lightweight
  experimental tests.

### NEXT VALIDATION

Compare pools with approximately equal expectation but different face
composition/variance, then repeat the pool progression probe on a second
Training B profile. Only after that should terrain and CTL-reserve conversion
be consolidated.


## Equal-expectation / different-variance comparison

### PROTOCOL

Using the same fixed Training B physiology profile as the preceding pool
progression probe, compare three pairs of pools with equal expected totals but
different face composition and variance. Each pool is run for 20 seeds with
the same normalized-cost rule, CTL 100, six flat segments and ADAPTIVE policy.
Total: 120 Race V2 runs.

### RESULTS

| Pair | Pool | E(pool) | Variance | Finish rate | Mean score | Mean spend |
|---|---|---:|---:|---:|---:|---:|
| E18 | 4d8 | 18.0 | 21.00 | 85% | 77.60 | 12.350 |
| E18 | 2d6+2d10 | 18.0 | 22.33 | 100% | 83.35 | 12.667 |
| E22.5 | 5d8 | 22.5 | 26.25 | 100% | 103.00 | 10.133 |
| E22.5 | 3d6+1d10+1d12 | 22.5 | 28.92 | 100% | 103.70 | 10.133 |
| E27 | 6d8 | 27.0 | 31.50 | 100% | 126.70 | 8.444 |
| E27 | 3d6+3d10 | 27.0 | 33.50 | 100% | 126.85 | 8.444 |

### INTERPRETATION

- **RESULT:** At E(pool)=18, the higher-variance pool (2d6+2d10) improves
  completion from 85% to 100% and mean score by 5.75.
- **RESULT:** At E(pool)=22.5 and 27, all courses finish; score differences
  between the lower- and higher-variance pool are small (0.70 and 0.15).
- **HYPOTHESIS:** Variance matters most near the viability boundary, where
  additional high-roll options can rescue a course. At higher expected totals,
  the completion ceiling hides most of the difference.
- **LIMIT:** Only one physiology profile, one policy and three pool pairs are
  tested. Face composition changes more than variance alone, so this is
  evidence of a distribution-shape effect, not a pure variance coefficient.
- **CI:** Run `42894254229` passed 138 primary tests and 89 lightweight
  experimental tests.

### NEXT VALIDATION

Repeat the equal-expectation comparison on a second Training B profile and
with a non-flat terrain profile. Then consolidate the cost unit and CTL reserve
mapping. Keep the normalization experimental until those checks are complete.
