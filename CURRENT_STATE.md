# Run It — Current State

Last consolidated: 2026-11-11
Canonical branch: main

This snapshot does not replace the GDD; AGENTS.md defines the authority hierarchy.
Development roadmap: DEVELOPMENT_PLAN.md.

## TRAINING B — CURRENT IMPLEMENTATION SNAPSHOT

- Active Training B rolls N−1 dice and supports Keep, Add, Reroll and Add+Reroll.
- Final dice energy is partitioned exactly between EF, Seuil and VMA.
- Dice-derived fatigue is committed before session/bust resolution.
- Successful sessions add adaptation XP; a bust cancels adaptation for the busted
  session and later sessions but does not undo dice-derived fatigue.
- Physiological progression uses three energy/speed coordinates, strictly
  increasing EF < Seuil < VMA. At a milestone, the player chooses speed at fixed
  energy or lower energy at fixed speed.

## RACE V2 — SEGMENT INTEGRATION

- physiology_grid.py converts effective energy to speed using the Training B
  curve and integer grid.
- race_turn.py reuses Training B's N−1 dice and player-selected dice actions.
- VMA energy clips actual segment expenditure; terrain changes effective energy
  but not reserve debit.
- The segment adapter accepts an externally supplied reserve.

## RACE RESERVE — TRAINING PREPARATION (2026-11-11)

- Training B records cumulative committed energy separately for EF, Seuil and
  VMA. Counters update after budget validation and before session resolution,
  so energy invested in a busted session still counts.
- Adaptation XP remains governed by successful session resolution; busted
  sessions contribute no adaptation.
- experiments/current/race_engine_v2/race_reserve.py provides a deterministic
  pre-race preview with per-track saturation, training-turn normalization,
  race-segment scaling and a bounded freshness bonus.
- Course segment counts are 7 / 10 / 13 / 16 for 5 km / 10 km / half /
  marathon. Course energy targets and numerical reserve/freshness calibration
  remain OPEN; no arbitrary balance values are hard-coded.
- The legacy longitudinal Race runner is not migrated by this change.

## OPEN

- Calibrate course-specific EF / Seuil / VMA energy targets and reserve scale.
- Calibrate freshness threshold, rate, cap and minimum preparation ratio.
- Integrate reserve preview into the full longitudinal Race V2 runner and UI.
