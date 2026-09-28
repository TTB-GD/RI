# EXP R1-B — Local Difficulty

**EXPERIMENTAL ONLY.** FORM_PATTERN and Curve B are technical baselines here,
not CURRENT rules or final calibration choices.

## FACT

### Form control before R1-B

Existing R1-A2 PATTERN / SL-off data were sufficient; no preliminary campaign
was rerun. The three signals use identical seeded rolls across policies, so the
configuration means were consolidated by pool.

| Pool | E[FormSignal] | E[FinalForm] |
|---|---:|---:|
| 6d6 | 0.230 | 0.690 |
| 4d8+1d6 | 0.143 | 0.430 |
| 2d10+4d6 | 0.179 | 0.536 |
| 1d8+3d6 | 0.127 | 0.382 |

The maximum observed gaps are 0.103 per signal and 0.308 per three-signal Form.
They are visible but not a qualitatively separate reserve regime. No arbitrary
acceptance threshold was introduced and no pattern threshold was recalibrated.
**Technical decision: control acceptable to proceed with R1-B**, while retaining
the inequality as an experimental limitation.

### Rule and fixtures implemented

- At each segment: `load = chosen Production + local difficulty`, then
  `cost = CurveB(load)`. Score remains chosen Production only.
- The entire profile is public. Policies receive current difficulty and the
  remaining profile, but never future rolls/signals or final reserve before S3.
- Difficulty has no state or recovery rule. Its only memory is cumulative spent
  reserve.
- Length 6: FLAT `0,0,0,0,0,0`; EARLY `0,3,3,0,0,0`; LATE
  `0,0,0,0,3,3`.
- Length 9: FLAT `0,0,0,0,0,0,0,0,0`; EARLY `0,3,3,0,0,0,0,0,0`;
  LATE `0,0,0,0,0,0,3,3,0`; ROLLING `0,2,0,3,0,2,0,3,0`.
- Diagnostic SLOW/MAINTAIN/ATTACK compares the same seed/pool/length/policy and
  segment against FLAT: delta ≤−2 / −1..+1 / ≥+2. It never affects resolution.
- Plausible choices retain the R1-A2 10% efficiency window, now using
  `P / CurveB(P + D)`.

### Campaign actually executed

- R1-B0 smoke: 4 pools × length 6 × 3 profiles × 4 policies × 50 seeds =
  **48 configurations / 2,400 races**, 7.45 seconds. All 800 FLAT smoke races
  reproduced the flat resolver baseline.
- R1-B1: 4 pools, lengths 6/9, FLAT/EARLY/LATE plus ROLLING at length 9,
  4 unchanged policy identities, FORM_PATTERN, Curve B, SL off, freshness 0,
  CTL 100, seeds 0–499: **112 configurations / 56,000 races**, 121.09 seconds.
- All **16,000** main FLAT races reproduced the corresponding flat R1-A2 engine
  result exactly for rolls, signals, choices, costs, reserve, score, clamp and
  DNF. In addition, 24 comparable EFFICIENT/ADAPTIVE/GREEDY aggregate rows
  reproduced the committed R1-A2 score/median/DNF/clamp results; AGGRESSIVE was
  absent from R1-A2. The optional SL sub-experiment was not run because it was
  not needed to answer the terrain question.
- Detailed outputs (3.2 MB courses, 84.3 MB turns) were generated and ignored.

## OBSERVATION

### Terrain response paired against FLAT

Values average pools and both lengths (4,000 paired races per policy/profile).
`ΔP difficult` compares only the difficult segments; extra cost is the direct
sum of `C(P+D)−C(P)` at the terrain choices.

| Terrain | Policy | ΔP difficult | Δ score | Δ spent | Extra terrain cost | SLOW | MAINTAIN |
|---|---|---:|---:|---:|---:|---:|---:|
| EARLY | EFFICIENT | −2.59 | −5.18 | 0.00 | 0.00 | 87% | 13% |
| EARLY | ADAPTIVE | −0.05 | −1.70 | +0.52 | 0.83 | 1% | 99% |
| EARLY | AGGRESSIVE | −1.35 | −6.51 | +0.70 | 3.43 | 42% | 58% |
| EARLY | GREEDY | 0.00 | −10.03 | +3.58 | 5.10 | 0% | 100% |
| LATE | EFFICIENT | −2.61 | −5.22 | 0.00 | 0.00 | 87% | 13% |
| LATE | ADAPTIVE | −0.46 | −1.56 | +1.27 | 1.75 | 10% | 90% |
| LATE | AGGRESSIVE | −2.10 | −3.92 | +0.35 | 0.56 | 68% | 32% |
| LATE | GREEDY | −1.88 | −1.16 | +0.34 | 0.59 | 57% | 43% |

EFFICIENT slows by about 2.6 Production and stays on an equal-cost Curve-B
plateau: terrain extra cost and total spent delta are both zero. ADAPTIVE mostly
maintains, paying a modest cost, especially late. AGGRESSIVE maintains 58% of
EARLY difficult decisions and pays 3.43 extra reserve on average; LATE reserve
constraints instead force more slowing. GREEDY maintains every EARLY difficult
turn it reaches, pays 5.10 extra, and loses 10.03 score through later DNF/truncated
trajectories rather than through immediate moderation.

ATTACK is rare (0–1%) for every paired group: terrain generates a maintain-versus-
slow tradeoff, not a systematic incentive to increase Production.

### DNF, timing, and energetic memory

On FLAT, aggregate DNF is 0% EFFICIENT, 0% ADAPTIVE, 6.0% AGGRESSIVE, and 68.3%
GREEDY. EARLY raises these to 0%, 0.1%, 8.2%, and 75.5%. LATE yields 0%, 0%,
6.0%, and 70.7%. GREEDY therefore remains distinctly myopic and penalized.

At the first flat segment after a difficulty block, paired Production deltas are:

| Profile | EFFICIENT | ADAPTIVE | AGGRESSIVE | GREEDY |
|---|---:|---:|---:|---:|
| EARLY | 0.00 | −0.25 | −0.81 | −0.90 |
| LATE | 0.00 | −1.29 | −0.13 | −0.71 |

No terrain status persists at those segments. The negative deltas for three
policies therefore arise through spent reserve/legality and demonstrate a small
energetic memory. EFFICIENT avoided debt by slowing on the difficulty itself.

Comparing LATE minus EARLY with equal total difficulty:

| Policy | Δ score | Δ DNF | Δ spent | Δ terrain extra cost |
|---|---:|---:|---:|---:|
| EFFICIENT | −0.03 | 0.0 pp | 0.00 | 0.00 |
| ADAPTIVE | +0.14 | −0.1 pp | +0.75 | +0.92 |
| AGGRESSIVE | +2.59 | −2.2 pp | −0.35 | −2.87 |
| GREEDY | +8.86 | −4.8 pp | −3.24 | −4.52 |

Timing is almost neutral for EFFICIENT/ADAPTIVE scores but material for
AGGRESSIVE/GREEDY. EARLY occurs before reserve revelation and permits costly
commitments that later constrain or terminate those policies; LATE legality
already limits what can be paid.

### Form interaction in ADAPTIVE

For EARLY, negative/zero/positive Form groups show difficult-segment deltas
−0.02/−0.07/−0.06 and extra terrain costs 0.75/0.74/0.93. For LATE they show
−0.23/−0.61/−0.50 and extra costs 1.01/1.56/2.23. Positive Form supports the
largest extra spend, but the middle group's production reduction is slightly
larger than the positive group's. The interaction is observable through reserve
headroom but is not monotonic enough to infer a general player rule.

### Choice space

Across every executed turn, flat segments expose 1.83 plausible Productions on
average and difficult segments 1.86 under the 10% efficiency window. Exactly
one plausible choice occurs on 16.9% of flat and 13.8% of difficult turns.
Difficulty therefore does **not** collapse the technical choice window; it
slightly shifts which Productions occupy it. Raw available/payable counts remain
in `summary_r1b.csv` by configuration.

## R1-B RESULTS

1. **Does ADAPTIVE slow?** Slightly: −0.05 EARLY and −0.46 LATE on paired
   difficult turns; it mostly maintains and pays extra.
2. **Does EFFICIENT slow?** Yes, consistently by about −2.6, avoiding extra cost.
3. **Does AGGRESSIVE maintain more?** It maintains 58% EARLY, versus EFFICIENT's
   13%, while LATE affordability forces more slowing.
4. **What extra cost?** AGGRESSIVE pays 3.43 EARLY and 0.56 LATE; ADAPTIVE pays
   0.83/1.75; EFFICIENT pays zero at its chosen lower Production.
5. **Future reduction from reserve?** Yes for ADAPTIVE, AGGRESSIVE and GREEDY;
   paired post-difficulty deltas range from −0.13 to −1.29.
6. **Does timing matter?** Strongly for myopic/aggressive probes, weakly for the
   two prudent probes. Equal total difficulty does not imply equal trajectory.
7. **Form dependence?** Positive Form funds more extra terrain cost, especially
   LATE, but Production response is not strictly ordered by Form group.
8. **Is GREEDY penalized?** Yes: 68–76% DNF depending on profile and large EARLY
   cost/debt; it is not competitive longitudinally.
9. **Plausible choices under difficulty?** 1.86 average; 13.8% single-choice turns.
10. **Choice or tax?** Both behaviours exist: EFFICIENT trades score for equal
    cost, while ADAPTIVE/AGGRESSIVE sometimes pay to maintain. It is not only a
    uniform tax under these technical policies.

## INTERPRETATION

The minimal `P+D → CurveB` rule produces a legible maintain-versus-slow tradeoff,
and reserve alone carries a measurable consequence into later flat segments.
Timing meaningfully separates policies with different reserve discipline. This
supports retaining the formula as a **candidate experimental baseline**, not as
a CURRENT rule or a claim about human behaviour.

## LIMIT

- Artificial profiles contain only non-negative local values 0/2/3.
- Curve B only; it remains a technical baseline, not a final curve.
- No human test; all behaviours belong to deterministic technical policies.
- Full difficulty is known before departure.
- No descent, reserve recovery, Nutrition, wind, qualities, injury or character.
- FORM_PATTERN and CTL→reserve remain experimental.
- EARLY segments 2–3 straddle S3; the clamp convention still affects early
  commitment interpretation.
- DNF trajectories truncate per-turn comparisons, particularly GREEDY; paired
  metrics use only commonly reached difficult turns and report DNF separately.

## GAME DESIGN HANDOFF

1. **Natural slowing?** Yes for EFFICIENT and, more mildly, ADAPTIVE.
2. **Rational maintenance?** Observable: ADAPTIVE and AGGRESSIVE sometimes retain
   near-flat Production and accept explicit extra cost.
3. **Is reserve sufficient memory?** Mechanically yes in this sample; no extra
   persistent terrain state was needed.
4. **Useful early/late difference?** Yes for AGGRESSIVE/GREEDY; modest for
   EFFICIENT/ADAPTIVE. Whether that magnitude is desirable is a design decision.
5. **Form interaction without a new rule?** Yes through reserve headroom, though
   the measured response is not perfectly monotonic.
6. **Real but bounded choice space?** The diagnostic window remains near two
   choices and does not collapse under difficulty.
7. **Keep `Charge=P+D; Cost=C(Charge)` experimentally?** The evidence justifies
   keeping it as the next experimental candidate, not promoting it to CURRENT.
8. **Next test?** Terrain calibration is the nearest isolated question: compare
   the magnitude/frequency of 2 and 3 before adding Nutrition or quality effects.

No conclusion in R1-B changes CURRENT Game Design.
