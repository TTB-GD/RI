# HISTORICAL — Race Reserve / ancien modèle de préparation

**Status: HISTORICAL / SUPERSEDED AS RACE DESIGN (12 November 2026).** This document preserves the earlier Training-investment reserve proposal. It is not the active Race V2 specification and must not be used to override the `S0 + F - C` sustainability model in `RACE_V2_DESIGN.md`.

## 1. Purpose

Race reserve is the sustainable energy budget for the selected race. It comes
from Training preparation and residual fatigue, not CTL and not directly from
the Race dice pool.

The Race dice pool is expected to be stronger than the average Training pool.
It represents available segment-level effort options, not sustainable energy.
The player must calibrate each segment's effort against a visible reserve.

## 2. Course-specific objectives

Selecting a race exposes three preparation objectives: EF, Seuil and VMA.
These objectives are course-specific and independent of the player's
physiological curve (decision A). They are targets for Training energy, not
physiological capacity or adaptation XP.

| Race | Segments |
|---|---:|
| 5 km | 7 |
| 10 km | 10 |
| Half-marathon | 13 |
| Marathon | 16 |

Qualitative emphasis:

| Race | EF | Seuil | VMA |
|---|---|---|---|
| 5 km | Low | Medium | Very high |
| 10 km | Low–medium | Very high | Medium |
| Half-marathon | High | High | Low |
| Marathon | Very high | Medium | Low |

Exact energy targets remain OPEN and must be calibrated against Training B
trajectories. No numerical target values are promoted here.

## 3. Committed energy versus adaptation

Each Training B turn partitions final dice energy between EF, Seuil and VMA.
Three persistent counters record committed investment:
- training_energy_ef
- training_energy_threshold
- training_energy_vma

They update after budget validation and before session resolution. Thus a
busted session still counts as invested energy, while the busted session grants
no adaptation XP and no session-specific fatigue. Dice-derived fatigue remains
committed. Energy investment and physiological adaptation are distinct.

## 4. Saturation

Each course defines a target O_i for each track. For committed energy E_i:

C_i = min(E_i, O_i)

Surplus max(0, E_i - O_i) is visible as saturated investment and does not
increase reserve. Saturation is independent per track. The player may still
train a saturated track for adaptation or other effects, but that extra energy
does not increase reserve for the selected race.

The first implementation uses a hard cap. A diminishing-return curve may be
tested later if the transition proves too abrupt.

## 5. Preparation reserve

The initial executable conversion is:

Preparation reserve = round_half_up((sum(C_i) / T) × S × k)

where T is Training turns played, S is Race segments and k is an explicit
calibration scale. This normalizes energy investment by Training phase length,
then scales it to Race length. No second pool-size multiplier is applied:
pool quality already influences Training energy budgets.

This is a transparent baseline, not a calibrated final equation. A course
profile supplies its targets, segment count and k. Zero Training turns produce
zero preparation reserve.

## 6. Freshness / taper

Taper should emerge from Training fatigue management; there is no scripted
mandatory taper phase. Residual fatigue at Race start produces a bounded bonus
when a configurable minimum preparation ratio has been met:

Freshness = min(cap, round_half_up(max(0, fatigue_threshold - fatigue) × rate))

Below the minimum preparation ratio, the bonus is zero. This prevents a player
from replacing preparation with inactivity. Threshold, rate, cap and minimum
preparation ratio remain OPEN configuration.

## 7. Player-facing feedback

Before the Race, the player can inspect a deterministic breakdown:
- course objectives EF / Seuil / VMA;
- energy invested in each track;
- credited energy and saturated surplus per track;
- preparation ratio;
- preparation reserve;
- fatigue at start and freshness bonus;
- total reserve.

The same calculation must be used for preview and Race initialization. No
hidden random roll is involved.

## 8. Separation from physiology and Race resolution

The physiological curve remains the energy-to-speed conversion during Race.
Its VMA energy coordinate caps actual expenditure per segment. Reserve does
not add physiology coordinates or adaptation XP a second time.

The Race dice pool controls available effort choices; reserve controls
cumulative affordability. Terrain changes effective energy for speed conversion,
while reserve is debited by actual energy spent.

## 9. OPEN calibration and integration

1. Numerical EF / Seuil / VMA energy targets for each race.
2. Course calibration scale k (shared or course-specific).
3. Freshness threshold, rate, cap and minimum preparation ratio.
4. Integration into the full longitudinal Race V2 runner and player UI.
5. Human readability and strategic value of hard saturation versus diminishing
   returns.

The implementation is an auditable calculation primitive. It does not invent
course target numbers or migrate the legacy longitudinal Race orchestration.
