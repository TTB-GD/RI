# EXP R1-A — Race Engine V2 / flat terrain

**Status: EXPERIMENTAL ONLY.** Results describe technical policies under frozen
fixtures. They do not validate a CURRENT race rule or a human-player behaviour.

## FACT

### Protocol actually executed

- R1-A0: 3 priority pools × 2 lengths × Curve B × 3 policies × 50 seeds =
  **18 configurations / 900 races**. The smoke completed and every pool/length
  pair showed at least two distinct policy mean scores, so the stop condition
  was not triggered.
- R1-A1: **200 targeted configurations / 100,000 races**, each with seeds
  0–499. Curve contrast used 5 pools × 2 lengths × A/B/C × 4 policies with
  neutral freshness and SL off (120 configurations). SL and freshness contrasts
  each added 40 configurations on Curve B. Total run: **218 configurations /
  100,900 races**, 151.46 seconds.
- Lengths were 6 and 9. CTL was fixed at 100; base reserve was therefore 14 or
  20. Freshness was 0 in the curve/pool and SL contrasts, and +3 only in the
  freshness contrast. R1-A1 used EFFICIENT, AGGRESSIVE, ADAPTIVE and GREEDY.
- Exact form and granularity enumeration covered 1,728–129,600 raw outcomes per
  pool. Large reproducible outputs were 7.1 MB (`courses.csv`) and 150.0 MB
  (`turns.csv`) and are intentionally ignored. Compact results are versioned.

### Frozen fixtures

- Curves, inclusive upper bounds from `≤15, 16–18, 19–21, 22, 23, 24, 25, 26,
  ≥27`: A = `1,2,2,3,4,5,7,9,12`; B = `1,2,2,3,5,7,10,13,16`; C =
  `1,2,3,5,8,12,16,20,25`.
- CTL→reserve: `2 × segments + floor(CTL/50)`. Freshness: 0/+3. Form:
  LOW/NORMAL/GOOD/EXCEPTIONAL = -1/0/+1/+2; SL changes only LOW to 0.
- Form uses the exact per-pool distribution of the complete raw-roll sum, with
  attainable cumulative cut points nearest from above to 20%/70%/93%.
- Pools: required `6d6`, `4d8+1d6`, `2d10+4d6`; progression-reachable
  `1d8+3d6` and `1d12+1d8+4d6`. The latter two follow the real one-upgrade and
  four-concentrated-upgrade/CTL-100 bounds; required mixed pools remain mandated
  comparison fixtures, not claims about the automatic upgrader.

## OBSERVATION

### Policies and curves

Mean results below average the five pools and both lengths (5,000 races/cell).

| Curve | Policy | Mean score | DNF | Payable choices | Clamp | Final acceleration |
|---|---|---:|---:|---:|---:|---:|
| A | EFFICIENT | 108.70 | 0.0% | 17.98 | 0.0% | 37.5% |
| A | AGGRESSIVE | 129.34 | 2.6% | 16.77 | 0.5% | 13.4% |
| A | ADAPTIVE | 124.87 | 0.0% | 17.73 | 0.0% | 87.7% |
| A | GREEDY | 97.43 | 74.6% | 17.93 | 35.8% | 45.7% |
| B | EFFICIENT | 108.70 | 0.0% | 17.79 | 0.0% | 37.5% |
| B | AGGRESSIVE | 129.66 | 1.9% | 16.71 | 0.0% | 13.7% |
| B | ADAPTIVE | 124.83 | 0.0% | 17.56 | 0.0% | 87.7% |
| B | GREEDY | 91.47 | 76.3% | 17.97 | 48.0% | 47.3% |
| C | EFFICIENT | 108.70 | 0.0% | 17.53 | 0.0% | 37.5% |
| C | AGGRESSIVE | 121.48 | 6.4% | 16.41 | 1.6% | 12.2% |
| C | ADAPTIVE | 121.07 | 0.6% | 17.01 | 0.0% | 56.3% |
| C | GREEDY | 84.22 | 80.0% | 18.01 | 62.7% | 48.4% |

EFFICIENT stays below the costly zone in these fixtures, explaining its
curve-invariant aggregate. AGGRESSIVE obtains the highest mean on B but has a
small DNF risk. ADAPTIVE remains DNF-free on A/B and strongly accelerates at the
end. GREEDY spends heavily before the longitudinal constraint can govern it and
usually DNFs; its score includes only completed turns, so it is not competitive.

### Pool composition and granularity

| Pool | Full-roll EV | Variance | Mean distinct sums | Exact P=22 available | P=22 ±2 available |
|---|---:|---:|---:|---:|---:|
| 6d6 | 21.0 | 17.50 | 18.97 | 35.4% | 63.7% |
| 4d8+1d6 | 21.5 | 23.92 | 16.71 | 31.8% | 65.4% |
| 2d10+4d6 | 25.0 | 28.17 | 22.15 | 65.6% | 84.5% |
| 1d8+3d6 | 15.0 | 14.00 | 10.41 | 2.0% | 11.9% |
| 1d12+1d8+4d6 | 25.0 | 28.83 | 22.19 | 65.2% | 84.1% |

On neutral Curve B, `6d6` versus `4d8+1d6` yields 19.0 versus 16.7 available
choices on average despite EVs only 0.5 apart. Their ADAPTIVE scores are 123.1
and 124.8, while GREEDY DNF rates are 87.5% and 93.2%. `2d10+4d6` offers 22.2
distinct sums, ADAPTIVE score 144.0, and materially greater access to P=22; its
composition changes choice density as well as full-roll EV.

### Progressive form, SL, and clamp

Exact class frequencies were broadly similar for four pools: LOW 20.4–21.2%,
NORMAL 51.2–53.5%, GOOD 20.6–22.4%, EXCEPTIONAL 5.1–6.1%. `1d8+3d6` is the
visible discrete exception (26.0%, 48.0%, 21.9%, 4.1%); it is not hidden or
reweighted.

Across 5,000 neutral Curve-B ADAPTIVE races, final-form groups behaved as follows:

| Final Form | Races | Mean first 3 P | Mean later P | Mean score |
|---|---:|---:|---:|---:|
| <0 | 1,472 | 14.85 | 16.76 | 119.73 |
| =0 | 1,292 | 15.53 | 17.17 | 123.46 |
| >0 | 2,236 | 16.50 | 17.76 | 128.98 |

The groups differ already in the first three turns because signal is correlated
with raw roll strength, so these figures demonstrate association and policy
response, not a causal estimate of Form alone.

On Curve B, SL changed mean score by 0.00 / +1.75 / +1.36 / +1.38 for
EFFICIENT / AGGRESSIVE / ADAPTIVE / GREEDY. It reduced AGGRESSIVE DNF by 1.94
percentage points and GREEDY DNF by 1.18 points; other DNF changes were zero.
It added 0.16–0.65 mean remaining reserve. Freshness +3 increased the respective
scores by 0.00 / 2.55 / 3.63 / 5.10 and reduced DNF by 0 / 0.8 / 0 / 4.5 points.

The clamp is policy-driven: 0/25,300 EFFICIENT, 0/25,300 ADAPTIVE,
101/25,000 AGGRESSIVE (0.4%), and 11,879/25,300 GREEDY (47.0%) over the full
run. It is more common at length 6 (13.9%) than 9 (9.8%), and for the two
high-power six-die pools (~20%) than `1d8+3d6` (0.1%). Thus the aggregate clamp
is not rare, but it is absent in the central and conservative probes and flags
the intended pathology of unrestricted early GREEDY spending.

## INTERPRETATION

- The kernel creates a bounded but nontrivial menu (about 10–22 distinct sums)
  and makes composition observable rather than collapsing a pool to EV.
- Longitudinal depth is visible under these policies: GREEDY is decisively
  different and usually fails; EFFICIENT, AGGRESSIVE, and ADAPTIVE produce
  distinct moderation, attack, and late-acceleration profiles.
- Convexity creates pacing pressure without a regularity score. However, this
  campaign does **not** establish that irregularity itself causes higher cost;
  both production level and policy co-vary with trajectory variance.
- B is a usable middle contrast: it permits some costly choices and separates
  policies without C's higher DNF. A/B are nearly identical for EFFICIENT and
  ADAPTIVE means, so the evidence does not justify selecting B as a winner.
- Progressive Form changes the ADAPTIVE target and observed trajectories, but
  the raw-roll/form correlation means a dedicated local counterfactual would be
  needed to isolate the adjustment's causal contribution.

## LIMIT

- Flat terrain only; no Difficulty, nutrition, wind, injuries, qualities, or
  complete training integration.
- CTL→reserve and direct freshness are experimental fixtures. Neither derives
  from Fatigue V1.
- Full-roll-sum quantile classification is a technical convention, not validated
  Form design; its discreteness is particularly visible for `1d8+3d6`.
- Policies are deterministic probes, not players. Their heuristics materially
  shape every policy comparison.
- Curves A/B/C are not finally calibrated. No oracle or human comparison ran.
- The third-turn post-choice clamp is intentionally permissive and makes GREEDY
  pathology measurable; another timing convention is a DESIGN QUESTION.
- Score is accumulated Production only. A DNF's partial score is reported, not
  converted into an additional penalty.

## GAME DESIGN HANDOFF

1. **Several plausible Productions?** Yes: 10.4–22.2 distinct sums on average,
   and 16.4–18.0 payable choices across aggregate curve/policy cells.
2. **Bounded/readable?** Computationally bounded (at most 63 subsets here), but
   17–22 displayed sums may still require a future usability test.
3. **GREEDY inferior/different?** Yes; 74.6–80.0% aggregate DNF and lower partial
   scores than longitudinal probes.
4. **EFFICIENT versus ADAPTIVE distinct?** Yes: lower EFFICIENT score and 37.5%
   versus up to 87.7% final acceleration.
5. **B more interesting than A/C?** B separates costly aggression without C's
   DNF increase, but A/B similarity in two policies prevents a design verdict.
6. **Natural pacing without bonus?** Yes under the probes; no regularity term is
   in score. Causality between irregularity and cost remains unisolated.
7. **Moderation/attack/slowdown/final acceleration?** Yes across EFFICIENT,
   AGGRESSIVE, low-margin ADAPTIVE, and high-margin ADAPTIVE trajectories.
8. **Does Form alter decisions?** Policy logic and grouped trajectories say yes;
   a causal counterfactual remains needed.
9. **Clamp rare/frequent?** Zero for EFFICIENT/ADAPTIVE, 0.4% AGGRESSIVE, but
   47.0% GREEDY: rare for intended longitudinal probes, frequent as a control
   pathology.
10. **Does SL protect without becoming mandatory?** It removes only LOW and gives
    modest mean effects; no evidence makes it mandatory in these fixtures.
11. **Similar-EV pools differ?** Yes: `6d6` has 2.26 more sums on average than
    `4d8+1d6`, plus trajectory/DNF differences.
12. **Power only or control too?** Both: the high-EV pools also expose about 22.2
    sums and much greater access to the 18–25 zone.
13. **Any curve makes choices obvious?** No by raw option counts, though option
    count is not a direct measure of cognitively plausible choices.
14. **Combinatorial explosion?** No computational explosion at ≤6 dice; exact
    2^n−1 enumeration remained small. Display burden remains open.
15. **Proceed to R1-B?** The data justify another isolated experiment, provided
    it first targets clamp timing, Form counterfactuals, and player-facing menu
    readability rather than treating these fixtures as settled.

### Final question

**Qualified yes:** the kernel generates enough differentiated, longitudinal
behaviour to remain the next **experimental** base candidate. It is not ready to
become CURRENT: fixture calibration, Form causality/classification, clamp timing,
and usability still require user validation and further experiments.
