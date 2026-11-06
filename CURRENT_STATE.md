# Run It — Current State

Last consolidated: 2026-11-06  
Canonical branch: `main`

This snapshot does not replace the GDD; the authority hierarchy in `AGENTS.md` applies.

Development roadmap: see [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md).

## TRAINING CURRENT

- The persistent pool starts at `4d6`; cumulative CTL adds one d6 at 50 and
  another at 100, with gains becoming available on the following turn.
- Four successful Quality sessions upgrade one die along
  `d6 → d8 → d10 → d12`; these dice have no permanent face bonus
  (`0 / 0 / 0`).
- D99 caps Quality sessions (including SL), EF can repeat, each Quality entry is
  unique, Qualities cannot outnumber EF sessions, and a turn counts at most
  seven sessions.
- RPE Max marks the safe zone. Eligible Qualities above it may be chosen
  voluntarily and tested for risk; EF above RPE Max remains unavailable.
- Bust resolution preserves safe sessions, cancels later risky Qualities, and
  exposes an explicit player choice to redistribute eligible energy into
  accessible EF sessions, including an empty or partial choice.
- CTL, prerequisites and die progression use only sessions actually completed
  successfully after bust resolution and any EF redistribution.
- Training simulation uses a local, seedable/injectable RNG for dice-budget and
  bust-risk rolls, without reseeding Python's module-global random state. The
  merged tests cover seeded replay and global RNG isolation (PRs #29–#31).
- Session logs distinguish each occurrence, including repeated session names,
  and identify the origin of redistributed EF sessions (PR #30).
- D99 static coverage audit: `tests/test_d99_table.py` defines independent
  expected fixtures for all 23 CURRENT signatures from the GDD: 5 at four dice,
  7 at five dice and 11 at six dice. It checks exact table equality and the
  `session_outcome` result for each signature. The three-die convention is
  characterized separately and remains OPEN / IMPLEMENTATION POLICY.
- CI confirmation: workflow [Tests #42254642083](https://github.com/TTB-GD/RI/actions/runs/42254642083)
  passed on `main` at commit `40151114` (2026-11-06). The run completed the
  98-test unit suite, JSON evidence validation and 80 lightweight experimental
  tests. B3 is therefore closed for the 4/5/6-die CURRENT signatures; this does
  not close or validate the separate three-die convention.

## FATIGUE — IMPLEMENTATION STATUS

- The current Training simulation computes `energy_and_fatigue(energy_effective,
  TN)` after bust resolution and any EF redistribution. The quasi-Fibonacci
  function is also used in the weighted selector's utility calculation; the
  simulation records per-turn and cumulative fatigue diagnostics.
- This is not the complete persistent Fatigue V1 system described as
  EXPERIMENTAL in the GDD. The `Player` state has no persistent fatigue field,
  and the recorded fatigue does not regulate later turns, reserve availability,
  bust risk or session eligibility.
- The D1 working design proposes a different decomposition based on the final
  dice result, excess Quality load and session-specific penalty. Those rules
  remain WORKING DESIGN / NON NORMATIVE and are not implemented in the current
  Training path. See `D1_TRAINING_WORKING_DESIGN.md`.

## RACE V2 CURRENT / INTEGRATED

- `PhysiologyProfile(ef, threshold, vma)` validates `EF < Seuil < VMA`.
- `physiological_cost` gives the floor `C(x) = EF` for every `x <= EF`, then
  uses the continuous experimental slopes 2 and 3, and rejects `x > VMA`.
- Race V2 resolves local `Charge = Production + Difficulty`, scores Production
  only, and treats `Charge <= VMA` as its hard physiological legality boundary.
- The experimental longitudinal runner in
  `experiments/current/race_engine_v2/core.py` can consume a profile directly:
  generated subset sums are filtered by Charge before the separate Reserve
  affordability filter. Its multi-segment orchestration, Reserve, Form,
  Freshness and policies remain EXPERIMENTAL; this does not make the complete
  Race loop a CURRENT production gameplay path.
- SPEC and the complete Training-to-profile conversion remain absent.

## EXPERIMENTAL CONSERVED

- The 2/3 slopes remain calibration, not final balance.
- The reused S1–S3 progressive Form reveal, S3 post-choice Reserve clamp, S4+
  payable filter and DNF flow remain an experimental baseline.
- `base_reserve = race_length × 2 + floor(CTL / 50)`, FORM_SUM/FORM_PATTERN
  (with FORM_PATTERN as the migration reference), direct Freshness fixtures,
  LOW protection by SL, and EFFICIENT/AGGRESSIVE/ADAPTIVE/GREEDY are experimental.
- Curve A/B/C remain available through the explicit legacy path, preserving the
  R1-A, R1-A2, R1-B and R1-B2 harnesses and historical results.

## OPEN / IMPLEMENTATION GAPS

- The complete Training → EF/Seuil/VMA mapping is not implemented.
- Final calibration of slopes 2/3 and of Reserve, Form, Freshness and SL is open.
- SPEC remains OPEN and unimplemented in Race V2; Training's `Spec*` catalogue
  entries are still an explicit design/implementation gap.
- The selector's technical SL priority remains open.
- D99's three-die convention remains OPEN / IMPLEMENTATION POLICY; this audit
  made no change to it.
- B3 has complete static test coverage for four-, five- and six-die GDD rows;
  confirm the relevant CI run before marking the gate fully verified.

## HISTORICAL / TRACEABILITY

Prior Race, Fatigue, Training and SPEC campaigns keep their recorded status and
results. No historical campaign is retroactively described as using the native
profile path.

## REPOSITORY CONVENTION

- `tests/` contains current behavior tests.
- `experiments/current/` contains experimental harnesses still informing open questions.
- `experiments/archive/` contains retained historical experiments.

## NEXT TARGETS

1. Treat B3 as closed for the 4/5/6-die CURRENT signatures on the successful
   2026-11-06 CI run; keep the three-die convention explicitly open.
2. Formalize and validate C1/C2, using `D1_TRAINING_WORKING_DESIGN.md` as
   preparatory non-normative material rather than as a selected Training model.
3. Decide Training target A/B/C (D1) before defining the Training-to-profile
   mapping.
4. Calibrate Reserve/Form/Freshness/SL and the physiological slopes after the
   minimum integrated loop is specified; resolve the remaining SPEC and SL
   questions at the appropriate design gates.
