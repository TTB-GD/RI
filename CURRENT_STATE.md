# Run It — Current State

Last consolidated: 2026-11-12
Canonical branch: main
Documentation snapshot updated after Race V2 dice-session integration (PR #67).

This file describes the code that exists, not every rule that has been designed.
The GDD is authoritative for validated design; `docs/game-design/RACE_V2_DESIGN.md`
contains the detailed Race V2 specification; DEVELOPMENT_PLAN.md tracks gaps and
the next work. No Training-to-Race end-to-end integration is claimed.

## TRAINING B — IMPLEMENTATION SNAPSHOT

- `training_v2/` is the active development base for Training B.
- It remains a one-player terminal prototype, not a multiplayer or graphical game.
- The current prototype has a persistent dice pool, EF / Seuil / VMA physiology,
  session resolution, adaptation and fatigue-related state.
- The Training B design is not yet fully integrated into the Race V2 prototype.
- See `training_v2/README.md` and the relevant experiment reports for exact
  implementation limits. Experimental harness outcomes are not automatically
  promoted to design rules.

## RACE V2 — MULTI-SECTOR PROTOTYPE

**Status: PROTOTYPE / EXPERIMENTAL.** The isolated implementation is in
`experiments/current/race_v2_prototype/`.

Implemented in the prototype:

- 5 km / 10 km / half-marathon / marathon lengths: 7 / 10 / 13 / 16 sectors;
- explicit integer energy-to-speed table supplied through player configuration;
- sector resolution with VMA expenditure and conversion caps, signed terrain,
  aspiration bonus, EF floor for positive expenditure and zero-spend no-op;
- cumulative sustainability balance using initial credit, revealed form and
  actual sector consumption;
- 3d6 form-of-day classification, category recipes and card decks;
- scheduled card reveals, including reveal-before-dice at the start of a sector;
- cumulative integer score, adjacent-gap groups, hare status and aspiration;
- full dice-pool roll, individual rerolls, free subset selection (including
  empty selection), and global non-regenerating reroll capital;
- two-phase orchestration: prepare/reveal/roll, then validate decisions and
  resolve the sector;
- independent seeded RNG streams per player and atomic validation of decisions.

PR #67 integrated the dice decisions into the multi-sector Race V2 prototype.
The presence of tests in the repository does not by itself assert their latest
CI execution status; consult GitHub checks for a specific run.

## TRAINING → RACE — IMPLEMENTATION GAPS

The prototype still receives explicit Race configuration. It does not yet
derive all Race inputs from a real Training B player state:

- physiological integer table and EF / Seuil / VMA coordinates;
- race-specific AS (`specific_pace`);
- initial sustainability credit `S0`;
- dice sizes from the persistent Training pool;
- affûtage tier from residual Training fatigue.

The current Race prototype accepts `dice_sizes` and `affutage_level` as
configuration inputs. The mapping from residual fatigue to affûtage tier is not
implemented. No automatic Training-to-Race conversion is claimed.

## DESIGN / CALIBRATION STATUS

- Race V2 rules are consolidated in `docs/game-design/RACE_V2_DESIGN.md` and
  summarized normatively in `Run It - GDD.md`.
- Curve shift per sustainability point is an experimental starting parameter.
- Form deck distributions, terrain values, reroll-capital balance and overall
  duration/decision density require playtesting or controlled experiments.
- The former Training-investment reserve formula in
  `docs/game-design/RACE_RESERVE_DESIGN.md` is superseded as Race design by
  the 2026-11-12 `S0 + F - C` model. The file is retained for historical
  traceability, not as a competing active specification.
