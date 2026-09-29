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
