# Run It — Current State

Last consolidated: 2026-09-29
Canonical branch: `main`

This snapshot does not replace the GDD; the authority hierarchy in `AGENTS.md` applies.

## CURRENT / INTEGRATED

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
- The selector's technical SL priority and D99 three-die convention remain open.

## HISTORICAL / TRACEABILITY

Prior Race, Fatigue, Training and SPEC campaigns keep their recorded status and
results. No historical campaign is retroactively described as using the native
profile path.

## REPOSITORY CONVENTION

- `tests/` contains current behavior tests.
- `experiments/current/` contains experimental harnesses still informing open questions.
- `experiments/archive/` contains retained historical experiments.

## NEXT TARGETS

1. Define the minimal Training-to-profile mapping.
2. Calibrate Reserve/Form/Freshness/SL and the physiological slopes.
3. Resolve the remaining SPEC, SL selector and D99 convention questions.
