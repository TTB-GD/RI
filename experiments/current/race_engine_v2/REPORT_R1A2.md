# EXP R1-A2 — Form Pattern Normalization

**EXPERIMENTAL ONLY.** FORM_SUM remains the experimental R1-A baseline;
FORM_PATTERN is a controlled counterfactual, not a CURRENT rule.

## FACT

### Implementation

- The race resolver now accepts `form_mode="SUM" | "PATTERN"`. No other race,
  policy, energy, reserve, clamp, scoring, DNF, pool, length, or RNG rule changed.
- FORM_SUM retains the exact R1-A sum thresholds and mapping.
- FORM_PATTERN extracts: maximum multiplicity, exact pair count, repeated-group
  count, triple/two-pair/full/four-kind flags, longest consecutive run, and
  distinct-value count. It uses neither raw sum nor chosen Production.
- Structural motif points are
  `3×(max multiplicity−1) + 2×repeated groups + 2×two-pairs + 3×full +
  4×four-kind + 2×max(0, run−2)`. The reported integer packs those points as
  `motif_points×100 + run×10 + distinct_values`; the final two fields only break
  structural ties.
- Each pool is enumerated exactly (1,728–129,600 raw outcomes). Attainable
  score thresholds nearest the 20%/70%/93% cumulative targets define the four
  classes. No sum-based tie-break or forced random split is used.
- The diagnostic plausible-choice count retains Productions whose `P/C(P)` is
  at least `(1−margin)` of the best payable efficiency. Margins 5%, 10%, and 20%
  are reported; no policy reads this metric.

### Campaign actually executed

- Curve B, freshness 0, CTL 100; pools `6d6`, `4d8+1d6`, `2d10+4d6`,
  `1d8+3d6`; lengths 6/9; ADAPTIVE/EFFICIENT/GREEDY; SL off/on; SUM/PATTERN.
- **96 configurations × 500 seeds = 48,000 races**, seeds 0–499, using paired
  seeds across modes. Runtime: **142.73 seconds**.
- Explicit SUM-versus-default comparisons covered **24,000 SUM races**. Compact
  score/DNF/clamp comparisons against the committed R1-A summary covered 48
  matching rows. No divergence was found.
- The 29.5 MB detailed turn CSV was generated and ignored. Only compact outputs
  are versioned.

## OBSERVATION

### Correlations — global paired campaign

| Mode | Metric | Pearson | Spearman |
|---|---|---:|---:|
| SUM | signal ↔ raw sum | 0.741 | 0.728 |
| PATTERN | signal ↔ raw sum | **−0.109** | **−0.104** |
| SUM | signal ↔ max accessible P | 0.741 | 0.728 |
| PATTERN | signal ↔ max accessible P | **−0.109** | **−0.104** |
| SUM | signal ↔ chosen P | 0.390 | 0.346 |
| PATTERN | signal ↔ chosen P | **−0.057** | **−0.053** |
| SUM | final Form ↔ final score | −0.009 | −0.033 |
| PATTERN | final Form ↔ final score | 0.031 | 0.023 |
| SUM | final Form ↔ final reserve | 0.399 | 0.511 |
| PATTERN | final Form ↔ final reserve | 0.177 | 0.383 |

`max accessible P` equals raw-roll sum because all faces are positive and the
full non-empty subset is legal before energy filtering. The two first
correlations are therefore necessarily identical, not independent evidence.
Pool-level PATTERN Pearson signal↔sum ranges from 0.000 (`6d6`) to −0.342
(`2d10+4d6`); this residual dependence comes from structural frequencies in
mixed die ranges, not from a sum feature.

### Exact normalized class frequencies

| Pool | Mode | LOW | NORMAL | GOOD | EXCEPTIONAL |
|---|---|---:|---:|---:|---:|
| 6d6 | SUM | 20.6% | 51.5% | 21.9% | 6.1% |
| 6d6 | PATTERN | 15.4% | 53.1% | 26.2% | 5.2% |
| 4d8+1d6 | SUM | 21.2% | 51.2% | 22.4% | 5.1% |
| 4d8+1d6 | PATTERN | 18.8% | 52.4% | 23.2% | 5.6% |
| 2d10+4d6 | SUM | 20.4% | 53.5% | 20.6% | 5.5% |
| 2d10+4d6 | PATTERN | 20.2% | 48.1% | 24.3% | 7.4% |
| 1d8+3d6 | SUM | 26.0% | 48.0% | 21.9% | 4.1% |
| 1d8+3d6 | PATTERN | 18.4% | 59.7% | 13.9% | 7.9% |

The discrete distributions prevent every target band from being met: notably
`1d8+3d6` has too much NORMAL and too little GOOD, while `6d6` has low LOW and
high GOOD. These deviations are exposed rather than artificially split.

### Future effect, policies, SL, and clamp

Across pools/lengths/SL, mean ADAPTIVE score was 120.68 (SUM) versus 120.63
(PATTERN); DNF remained 0%. With SL off, PATTERN changed the paired ADAPTIVE
choice trajectory in 93.4% / 84.3% / 96.7% / 68.9% of races for `6d6` /
`4d8+1d6` / `2d10+4d6` / `1d8+3d6`. Mean score deltas were respectively
+0.22 / −0.08 / −0.27 / −0.13. Thus decisions change frequently, while average
performance barely changes.

For unclamped SL-off ADAPTIVE, final Form↔reserve Pearson is exactly 1.0 by the
reserve equation. Mean per-configuration Form↔score Pearson falls from 0.655
(SUM) to 0.443 (PATTERN): PATTERN retains a measurable association through
future reserve/decisions but removes much of the immediate-roll redundancy.

SL under PATTERN adds +0.56 mean Form/reserve to ADAPTIVE and +1.25 mean score,
with no ADAPTIVE DNF or clamp change. For GREEDY it changes mean score +0.68,
DNF −0.6 percentage point, clamp −1.6 points, and final reserve +0.30. SUM's
corresponding Form increase is +0.66. SL remains a modest downside protection;
the +2 ceiling is unchanged by construction.

Clamp remains absent for ADAPTIVE and EFFICIENT. GREEDY clamp is 38.89% under
SUM and 39.26% under PATTERN, a +0.37-point change: no strong distributional
shift was observed.

### Diagnostic rolls

All examples are exact `6d6` outcomes; structure is computed before selection.

| Case | Roll | Sum | Key structure | Score | PATTERN | SUM | Accessible P |
|---|---|---:|---|---:|---|---|---|
| Low sum + good pattern | `1,1,1,1,1,1` | 6 | six-kind, 1 distinct | 2111 | EXCEPTIONAL | LOW | 1–6 |
| High sum + plain pattern | `1,1,4,5,6,6` | 23 | two pairs, run 3 | 1134 | NORMAL | NORMAL | 1–19, 21–23 |
| High sum + good pattern | `1,1,3,6,6,6` | 23 | pair + triple/full | 1513 | GOOD | NORMAL | 1–23 |
| Low sum + plain pattern | `1,1,1,2,2,2` | 9 | two triples | 1222 | NORMAL | LOW | 1–9 |

These examples demonstrate both directions: equal sum 23 can produce different
PATTERN classes, and a very low sum can be structurally EXCEPTIONAL.

## FORM_SUM VS FORM_PATTERN

1. **Signal↔sum:** Pearson 0.741 versus −0.109; Spearman 0.728 versus −0.104.
2. **Signal↔max P:** identical values because max subset sum equals raw sum.
3. **Signal↔chosen P:** Pearson 0.390 versus −0.057.
4. **Future effect:** yes mechanically on reserve and observably on trajectories;
   mean score impact is small rather than uniformly beneficial.
5. **ADAPTIVE decisions:** 68.9–96.7% of paired trajectories differ by pool.
6. **SL:** still modest; +0.56 Form/reserve and +1.25 ADAPTIVE score under
   PATTERN, without changing positive mappings.
7. **Clamp:** essentially stable overall; GREEDY changes only +0.37 point.
8. **Class comparability:** acceptable for two pools, visibly imperfect for
   `6d6` and especially `1d8+3d6` because attainable structural bins are coarse.
9. **High-sum/weak-Form and low-sum/strong-Form cases:** both exist exactly; the
   diagnostic examples show them directly. Broader class frequencies remain in
   `pattern_stats_v2.csv`; the examples alone do not estimate case frequency.
10. **Distinct information:** yes, substantially; residual mixed-pool
    correlations and uneven class bands prevent calling it fully normalized.

## CHOICE SPACE

Mean available Productions are **17.07**. The efficiency-window diagnostic
reduces this to **1.00 / 1.84 / 3.43** plausible Productions at 5% / 10% / 20%
margins. The conclusion is sensitive to the arbitrary window: at the primary
10% fixture the menu is small, but this is not a player-valid definition of a
meaningful choice and is not used by any policy.

## INTERPRETATION

FORM_PATTERN strongly reduces the immediate double advantage embedded in
FORM_SUM and still changes future reserve-aware decisions. Its negligible mean
score delta is desirable for isolation but does not prove that the information
will feel meaningful to players. The negative mixed-pool correlations and class
band deviations indicate that this particular structural score is a promising
probe, not a validated Form rule.

## LIMIT

- Structural weights and tie packing remain experimental.
- Rarity normalization is technical and discrete; it does not meet every target
  band and uses exact enumeration rather than human pattern perception.
- No human test and no causal claim that Form improves performance.
- Flat terrain only; no Difficulty, Nutrition, wind, or quality effects.
- CTL→reserve, freshness and all policies remain technical experimental fixtures.
- Global correlations duplicate paired signals across policies/SL by design;
  configuration and pool rows are supplied for inspection.
- Maximum accessible Production is mathematically the full positive roll, so it
  is not an independent opportunity metric in this kernel.

## GAME DESIGN HANDOFF

1. **Does PATTERN sufficiently reduce SUM's double advantage?** Numerically yes
   in this campaign: absolute Pearson signal↔sum falls from 0.741 to 0.109.
2. **Does Form remain useful without redundancy?** It changes most ADAPTIVE
   trajectories and reserve, but its player-facing usefulness is untested.
3. **Is SL clearer?** Its downside-only effect stays modest and mechanically
   isolated, but this does not validate SL design.
4. **Is decision load bounded?** The 10% technical window averages 1.84 options
   versus 17.07 raw sums; human plausibility remains unknown.
5. **Ready for R1-B Difficulty?** The decoupling result is clean enough to keep
   R1-B technically possible, but FORM_PATTERN should remain a switchable probe.
6. **Blocking point before R1-B:** no technical blocker; the unresolved design
   point is whether uneven structural class frequencies—especially `1d8+3d6`—
   are acceptable or require a user-approved alternative normalization.

No FORM_PATTERN rule is promoted to CURRENT by this report.
