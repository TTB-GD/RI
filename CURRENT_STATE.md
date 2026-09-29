# Run It — Current State

Last consolidated: 2026-09-29
Canonical branch: `main`
Integration milestone: `Integrated V2 baseline` (reference commit/PR recorded at task closure)

This file is the fast-entry snapshot for the current prototype state. It does
not replace the GDD; the authority hierarchy in `AGENTS.md` applies.

## CURRENT / INTEGRATED

The existing Training prototype still provides the persistent pool, CTL and die
progression, D99 planning constraints, risk/bust resolution and optional
player-chosen post-bust EF replacement described by the GDD and production tests.

Race V2 now has a deliberately small production boundary:

- `PhysiologyProfile(ef, threshold, vma)` validates `EF < Seuil < VMA`;
- `physiological_cost` is pure, has `C(EF) = 0`, is continuous at Seuil and
  explicitly rejects loads outside the integrated `EF..VMA` domain;
- a race segment resolves `Charge = Production + Difficulty`, applies the
  physiological cost, scores only Production and gives Difficulty no persistent
  state;
- SPEC, Position, Efficacité and AS42/AS21/AS10/AS5 have no active dependency in
  this integrated path.

This is the current integration frontier: future Training can produce a profile,
and Race V2 can consume it directly. The full experimental Training V2 harness
has not been promoted.

## EXPERIMENTAL

- The physiological slopes `2 / 3` are calibration parameters, not final balance.
- Race reserve construction, Form, policies, lengths, objectives and DNF flow
  remain experimental harness material under `experiments/current/race_engine_v2/`.
- Curve A/B/C remain unchanged there solely for reproducibility; they are not the
  native integrated physiological curve.
- Fatigue V1, Standard Training Player and automatic selection policies remain
  experimental and are not normative player behavior.
- Training V2 conventions such as D99_BONUS_ONLY, mandatory Q partition, one
  physiological gain per turn, milestones, quality costs and P_EF/P_BALANCED/
  P_QUALITY have not been promoted.

## OPEN / IMPLEMENTATION GAPS

- **SPEC is OPEN — NOT IMPLEMENTED** in Race V2. Training's existing `Spec*`
  catalogue entries are an explicit implementation/design gap, not a V2 rule.
- Legality and cost for `Charge > VMA` need a design decision. The integrated
  function reports the case as outside its domain; VMA is not silently made a
  Production cap because Difficulty also contributes to Charge.
- The complete Training → EF/Seuil/VMA progression mapping is not implemented.
- Reserve, Form, race objectives, the race role of SL and full multi-segment
  orchestration are not integrated design rules.
- The selector's technical SL priority remains an implementation/policy gap.
  The post-bust rule boundary already exposes and validates the player's EF
  choice; only a future user-facing interface is outside the current engine.

## HISTORICAL / TRACEABILITY

SPEC experiments (`training_v2_specific`, `race_efficiency_probe`,
`training_race_bridge`, `spec_local_curve_probe`) are retained without changing
their results and are marked as experimental probes of an OPEN question rather
than baseline or abandoned work.
Curve A/B/C and prior large Race/Fatigue/Training campaigns remain reproducible
experimental evidence; their figures are not CURRENT balance.

## REPOSITORY CONVENTION

- `tests/` contains tests of current prototype behavior.
- `experiments/current/` contains isolated work that still informs current open
  questions; explicit status labels prevent promotion into rules.
- `experiments/archive/` contains historical experiments when archived.

## NEXT TARGETS

1. Decide the domain behavior for Charge above VMA.
2. Define the minimal Training-to-profile mapping without promoting harness policy.
3. Decide Reserve/Form/SL boundaries before integrating full race orchestration.
4. Resolve the SL selector gap; treat any future post-bust UI separately from
   the already implemented choice-validation boundary.
