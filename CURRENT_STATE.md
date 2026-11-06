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
  `session_outcome` result for each signature. CI execution status has not been
  confirmed as part of this audit; do not infer passing CI from test presence.

## RACE V2 CURRENT / INTEGRATED

- `PhysiologyProfile(ef, threshold, vma)` validates `EF < Seuil < VMA`.
- `physiological_cost` gives the floor `C(x) = EF` for every `x <= EF`, then
  uses the continuous experimental slopes 2 and 3, and rejects `x > VMA`.
- Race V2 resolves local `Charge = Production + Difficulty`, scores Production
  only, and treats `Charge <= VMA` as its hard physiological legality boundary.
- The existing longitudinal engine now consumes a profile directly: generated
  subset sums are filtered by Charge before the separate Reserve affordability
  filter. SPEC and the complete Training-to-profile conversion remain absent.

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

1. Confirm CI execution of `tests/test_d99_table.py` and then close B3; keep the
   three-die convention explicitly open.
2. Define the minimal Training-to-profile mapping after the Game Design target
   has been decided.
3. Calibrate Reserve/Form/Freshness/SL and the physiological slopes.
4. Resolve the remaining SPEC and SL selector questions.
