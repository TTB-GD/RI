# EXP R1-B2 — Difficulty Magnitude × Frequency Calibration

**EXPERIMENTAL ONLY.** This calibration changes neither the R1-B engine nor
FORM_PATTERN, Curve B, reserve, scoring, CTL, freshness, SL, or policies.

## FACT

### Protocol actually executed

- Common fixtures: 9 segments, FORM_PATTERN, Curve B, CTL 100, freshness 0,
  SL off, pools `6d6` / `4d8+1d6` / `2d10+4d6` / `1d8+3d6`, four unchanged
  policies, paired seeds 0–499.
- R1-B2A: M0 plus M1/M2/M3/M4 with two central consecutive difficult segments:
  **80 configurations / 40,000 races**, 88.35 seconds. All 8,000 M0 courses
  reproduced the flat engine baseline; 16 aggregate flat rows also reproduced
  the committed 9-segment R1-B summary.
- Technical selection after A: D2 and D3. Both retained distinct policy
  responses, multiple plausible choices and no new non-myopic DNF regime. D1
  was milder; D4 caused 19.3% aggregate ADAPTIVE DNF despite a stable plausible-
  choice count. This selected test axes, not a winning Game Design rule.
- R1-B2B: D2/D3 at regularly distributed F2/F3/F4 plus one shared F0:
  112 result configurations.
- R1-B2C: P1/P2/P3 plus P0. P0 reused the already simulated F0 course objects;
  it was not simulated again. B+C therefore executed **160 configurations /
  80,000 races**, 180.39 seconds, while producing 176 result configurations.
  Its shared F0/P0 control likewise reproduced all 16 committed flat rows.
- Retained campaign total: **120,000 races**. Large detailed outputs were
  generated and ignored. A development aggregation bug on fully truncated turn
  columns was corrected before the retained A output; no rule or result fixture
  was recalibrated in response.

### Fixtures and diagnostics

- Magnitude: M1..M4 = `0,0,0,D,D,0,0,0,0`; M0 is flat.
- Frequency at D2/D3: F2 `0,D,0,0,0,D,0,0,0`; F3
  `0,D,0,0,D,0,0,D,0`; F4 `0,D,0,D,0,D,0,D,0`.
- Representative: P1 `0,1,0,1,0,1,0,1,0`; P2
  `0,0,2,0,0,2,0,0,0`; P3 `0,0,3,3,0,0,0,0,0`; P0 flat.
- Primary SLOW/MAINTAIN/ATTACK is strict paired delta `<0 / =0 / >0`.
- `forced_like` means plausible count ≤1 under the unchanged 10% efficiency
  window. It is diagnostic, not proof of a forced human choice.

## OBSERVATION

### Magnitude sweep

Values average four pools (2,000 races per policy/magnitude). `ΔP` applies only
to difficult turns and is paired to M0.

| D | Policy | ΔP | Extra cost | DNF | Plausible D | Forced-like D | SLOW | MAINTAIN | Post-D ΔP |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | EFFICIENT | −0.82 | 0.00 | 0.0% | 1.86 | 14% | 73% | 27% | 0.00 |
| 1 | ADAPTIVE | −0.00 | 0.06 | 0.0% | 1.86 | 14% | 0% | 100% | −0.02 |
| 1 | AGGRESSIVE | −0.56 | 0.67 | 5.3% | 1.86 | 14% | 44% | 56% | −0.17 |
| 1 | GREEDY | −0.45 | 0.73 | 73.2% | 1.86 | 14% | 29% | 70% | −0.41 |
| 2 | EFFICIENT | −1.71 | 0.00 | 0.0% | 1.87 | 13% | 86% | 14% | 0.00 |
| 2 | ADAPTIVE | −0.02 | 0.20 | 0.0% | 1.87 | 13% | 2% | 98% | −0.05 |
| 2 | AGGRESSIVE | −1.17 | 1.19 | 5.3% | 1.87 | 13% | 54% | 46% | −0.39 |
| 2 | GREEDY | −0.96 | 1.39 | 74.4% | 1.87 | 13% | 40% | 60% | −0.61 |
| 3 | EFFICIENT | −2.59 | 0.00 | 0.0% | 1.87 | 13% | 91% | 9% | 0.00 |
| 3 | ADAPTIVE | −0.04 | 0.75 | 0.0% | 1.87 | 13% | 4% | 96% | −0.22 |
| 3 | AGGRESSIVE | −1.83 | 1.59 | 5.3% | 1.87 | 13% | 59% | 40% | −0.55 |
| 3 | GREEDY | −1.51 | 1.99 | 75.9% | 1.86 | 14% | 46% | 53% | −0.77 |
| 4 | EFFICIENT | −3.57 | 0.00 | 0.0% | 1.86 | 14% | 94% | 6% | 0.00 |
| 4 | ADAPTIVE | −0.11 | 1.73 | **19.3%** | 1.86 | 14% | 8% | 92% | −0.54 |
| 4 | AGGRESSIVE | −2.54 | 1.91 | 5.3% | 1.86 | 14% | 64% | 36% | −0.66 |
| 4 | GREEDY | −2.15 | 2.50 | 77.6% | 1.86 | 14% | 52% | 48% | −1.08 |

D1 changes EFFICIENT/AGGRESSIVE decisions but is nearly neutral for ADAPTIVE.
D2 and D3 are **DISCRIMINATING**: identities remain separated, both slowing and
maintenance occur, and non-myopic DNF remains at its flat regime. D4 does not
collapse the efficiency-window count, so it is not `FORCING` by that diagnostic;
however, its 19.3% ADAPTIVE DNF is a clear over-severity warning under the fixed
reserve/policy fixtures. No magnitude causes plausible choices to collapse.
Policies do not fully converge even at D4, although EFFICIENT and AGGRESSIVE
slow progressively more.

### Frequency sweep

Values average all policies and pools; non-GREEDY DNF is reported separately.

| D | Frequency | Mean score | Non-GREEDY DNF | Spent | Extra cost | ΔP D | Plausible D | Forced-like D | Post-D ΔP | Final acceleration |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 129.03 | 2.1% | 16.79 | 1.16 | −0.77 | 1.86 | 14% | −0.09 | 58% |
| 2 | 3 | 127.96 | 2.1% | 16.91 | 1.39 | −0.85 | 1.86 | 14% | −0.14 | 42% |
| 2 | 4 | 126.77 | 2.1% | 16.98 | 1.67 | −0.89 | 1.87 | 14% | −0.19 | 44% |
| 3 | 2 | 126.94 | 2.4% | 17.05 | 1.76 | −1.17 | 1.87 | 13% | −0.14 | 57% |
| 3 | 3 | 125.42 | 2.3% | 17.22 | 2.06 | −1.30 | 1.87 | 13% | −0.24 | 36% |
| 3 | 4 | 123.57 | 2.3% | 17.34 | 2.42 | −1.37 | 1.87 | 13% | −0.30 | 39% |

F2 remains localized. F3 and F4 show **PROGRESSIVE_EROSION**: score falls,
spent/extra cost and post-terrain debt rise, and acceleration is less frequent.
Neither reaches `OVERLOADED`: non-GREEDY DNF is stable and forced-like rate does
not rise. Effects are larger at D3 than D2. Policy identities remain distinct at
F4: at D3, EFFICIENT/ADAPTIVE/AGGRESSIVE/GREEDY ΔP is
−2.61/−0.23/−2.09/−0.55 and extra cost is 0.00/1.75/3.80/4.14.

### Representative profiles

P1 and P2 both have raw difficulty sum 4; P3 has sum 6.

| Profile | Mean score | Non-GREEDY DNF | Spent | Extra cost | ΔP D | Plausible D | Forced-like D | Post-D ΔP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 132.54 | 1.8% | 16.37 | 0.00 | — | — | — | — |
| P1 | 129.80 | 1.9% | 16.66 | 0.87 | −0.43 | 1.86 | 14% | −0.10 |
| P2 | 129.48 | 1.8% | 16.74 | 0.93 | −0.76 | 1.87 | 13% | −0.19 |
| P3 | 127.03 | 1.8% | 16.96 | 1.66 | −1.16 | 1.87 | 13% | −0.48 |

- P1 produces mild progressive erosion across four small events; it is not
  trivial, but individual events are least salient.
- P2 produces clearer localized decisions than P1 despite equal `sum(D)`:
  larger slowing and roughly twice the post-difficulty Production debt.
- P3 is a readable severe block with the largest extra cost and post-block debt.
  It is not quasi-forced by plausible count or non-GREEDY DNF.
- The families are distinguishable quantitatively. The convex cost means equal
  raw difficulty totals do not imply equal effective terrain cost.

Policy detail reinforces this distinction. Under P1/P2/P3, EFFICIENT ΔP is
−0.82/−1.71/−2.60 with zero extra cost; ADAPTIVE is −0.06/−0.01/−0.03 and pays
0.45/0.23/0.63; AGGRESSIVE is −0.63/−1.12/−1.60 and pays 1.59/1.52/2.53.
GREEDY maintains 89%/93%/89% of reached difficult turns and pays
1.46/1.95/3.46, with 73.8%/74.6%/76.1% DNF.

## MAGNITUDE ANSWERS

1. **D1 changes decisions?** Yes for EFFICIENT/AGGRESSIVE; almost not for
   ADAPTIVE. It is a mild rather than wholly neutral signal.
2. **D2 preserves choices?** Yes: 1.87 plausible, 13% forced-like, distinct
   slow/maintain responses and no new prudent-policy DNF.
3. **D3 preserves slow and maintain?** Yes across policies: EFFICIENT strongly
   slows while ADAPTIVE mainly maintains and AGGRESSIVE splits 59%/40%.
4. **Does D4 become forcing?** Not by plausible-count/convergence, but it becomes
   outcome-severe for ADAPTIVE (19.3% DNF), so it is a calibration warning.
5. **Where does plausible count collapse?** Nowhere in D1–D4 under this metric.
6. **Where do policies converge?** No tested magnitude fully converges them.

## FREQUENCY ANSWERS

1. **Two segments localized?** Yes for D2/D3.
2. **Three create erosion?** Yes: lower score/acceleration and higher debt.
3. **Four overload?** No under the diagnostic criteria, though erosion grows.
4. **Magnitude dependence?** Yes; every frequency effect is stronger at D3.
5. **Policy distinction?** Preserved through F4.

## PROFILE ANSWERS

1. **P1 progressive erosion?** Yes, mild and distributed.
2. **P2 localized arbitration?** Yes, with stronger event response than P1.
3. **P3 tactical block/debt?** Yes; it has the largest extra cost and post debt.
4. **Distinct?** Yes, including P1 versus equal-total P2.
5. **Too weak?** P1 is mild, not null; whether it is perceptible is untested.
6. **Too forcing?** None by forced-like or non-GREEDY DNF in this campaign.

## CURVE B

The D1–D4 sweep identifies a usable experimental region under Curve B: D2 and
D3 remain discriminating while D1 is mild and D4 shows outcome-severity risk.
Therefore this experiment does **not** produce the condition “terrain
calibration unsuccessful under Curve B.” It also does not validate Curve B as a
final design curve.

## INTERPRETATION

Magnitude and frequency are not interchangeable. D2/D3 preserve policy identity
and bounded options; increased frequency then produces progressive reserve
erosion without a forced-choice or non-myopic DNF explosion. Several D1 events,
two D2 events and a D3 block produce distinguishable experiences. These are
technical observations, not final terrain rules.

## LIMIT

- No human test; plausible/forced-like metrics are technical proxies.
- Curve B, FORM_PATTERN, CTL→reserve and policies remain experimental.
- Only 9-segment, public, non-negative profiles were calibrated.
- No descent, Nutrition, wind, recovery, qualities, injury or character.
- GREEDY truncation means difficult-turn distributions include only reached
  paired turns; DNF is reported separately.
- The first failed report-generation pass encountered empty late-turn data for
  fully truncated configurations; the safe aggregation fix did not change race
  resolution or rerun calibration choices.

## GAME DESIGN HANDOFF

1. **Magnitude range with the clearest experimental space:** D2–D3. This is a
   technical range, not a selected final value.
2. **Playable frequency without decorative terrain:** F2 is localized; F3/F4
   create measurable erosion without overload in these fixtures.
3. **Small frequent versus few large:** Yes, P1/P2/P3 differ even when P1/P2
   share `sum(D)=4`.
4. **Real but bounded choices:** The proxy remains near 1.86–1.87 and rarely
   forced-like; policy responses remain distinct.
5. **Reserve as sole memory:** Still sufficient; post-difficulty deltas emerge
   without any terrain state.
6. **Can an experimental scale be frozen?** The data support carrying D1 as
   mild, D2 as medium and D3 as severe probes; D4 should remain a stress case.
   User validation is required before freezing even an experimental convention.
7. **Proceed to Nutrition?** Technically possible after that user decision, but
   a human-readability check of D1–D3 would reduce responsibility confusion.
8. **Reopen Curve B first?** Not required by these results; final calibration
   remains open.

No result is promoted to CURRENT Game Design.
