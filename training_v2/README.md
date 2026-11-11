# Training B — dose-based session resolution

**EXPERIMENTAL — active target architecture selected on 2026-11-07.** Training
CURRENT and the former direct-dice-to-session prototype are historical and are
not compatibility targets.

## Historical direct dice-to-session path — RETIRED

The old `training_v2.engine`, `programs`, `catalog` and console path assign
dice directly to sessions. They remain temporarily for regression
characterization only. They do not define Training B's active economy and
must not be extended as the new model.

The active turn path is `training_v2.turn.resolve_training_turn`:
dice decisions produce one conserved energy total; the player partitions it
between EF, Seuil and VMA; the player then selects exact-dose sessions from
the corresponding budgets. Session effects are resolved in plan order.

## Permanent session portfolio

- The initial acquired portfolio contains EF fondamentale, Tempo au seuil and Fractionné VMA.
- Catalogue options have a separate eligibility state and acquisition state. Unlocking an option only makes it eligible; the player must explicitly acquire it before it appears in program options.
- The prototype exposes `make_session_eligible(state, key)` and `acquire_session(state, key)`. These are event hooks for progression milestones and player choices; no automatic unlock thresholds or acquisition cadence are invented here.
- Successful EF, Seuil and VMA sessions now feed separate local progression counters. `PortfolioMilestone` maps a configurable track threshold to one or more eligibility unlocks; the player still has to acquire each option explicitly. A newly eligible option can be acquired after the turn and is usable from the next program selection.
- Unlock thresholds are injected configuration, not hard-coded balance. The prototype defines the mechanism but deliberately ships no default unlock schedule until those thresholds are arbitrated.
- Advanced EF/Seuil/VMA options from D1-S4 are present as **EXPERIMENTAL candidate fixtures**. Their costs, RPE, adaptations and fatigue are illustrative and uncalibrated.
- SL/SPEC catalogue options and the global progression rule are not implemented. SPEC remains a cross-cutting design concept, not an additional physiological axis in this prototype.
- The turn resolver and option enumerator both enforce the acquired portfolio. A merely eligible or unknown option cannot be played.

Run the console from the repository root:

~~~bash
python -m training_v2
~~~

## Initial catalogue fixtures — EXPERIMENTAL

| Session | Load | Cost | RPE | Adaptation | Fatigue | Per turn |
|---|---|---:|---:|---|---:|---:|
| EF fondamentale | EF | 2 | 2 | EF +1 | 0 | No general cap |
| Tempo au seuil | Quality | 4 | 4 | Seuil +1 | 0 | 1 |
| Fractionné VMA | Quality | 5 | 5 | VMA +1 | 1 | 1 |

Values are executable fixtures, not calibrated rules. Cost and RPE are independent fields. Adaptations are fixed per successful session and are not multiplied by energy.

## Accounting retained provisionally

- Energy assigned to EF-load sessions advances EF volume progression.
- Successful Quality sessions advance Q progression by their catalogue energy cost.
- Only successfully completed Quality sessions contribute their unused energy to the experimental SPEC counter. SPEC itself remains OPEN and this accounting is temporary.
- A bust stops subsequent session resolution; the busted session and later unexecuted sessions contribute no adaptation, progression, realized EF/Quality load, SPEC remainder or session-specific fatigue.
- Fatigue still uses the existing experimental blackjack term, the excess Quality-over-EF term, and specific session fatigue. Calibration is deferred.

## Known limitations

- This is a one-player terminal prototype, not multiplayer or a graphical UI.
- Initial profile is EF 6 / Seuil 8 / VMA 10.
- Volume milestones remain experimental B2 fixtures and add dice at selected thresholds; physiological EF gains come from successful EF sessions, not from a second automatic EF increase. Fatigue remains experimental.
- SL/SPEC acquisition, global progression, combinations, and Training-to-Race conversion are not implemented. The local EF/Seuil/VMA portfolio lifecycle is prototyped, but progression thresholds and acquisition cadence remain OPEN.
- Risk uses the largest persistent die as the risk-roll range; this remains experimental.

Run tests:

~~~bash
python -m unittest discover -s tests -p 'test_training_v2*.py' -v
~~~


## Q1–Q55 migration status — 2026-11-11

The implementation above is the historical direct-dice-to-session prototype. It
does **not** yet implement the decisions consolidated in
`docs/game-design/TRAINING_B_DECISIONS.md` and is not a compatibility target.

The first replacement building block is `TrainingEnergyBudget`: it conserves
the final dice energy across EF, Threshold and VMA, with Threshold + VMA forming
the Quality budget. Session-dose allocation is deliberately not included in
this primitive.

Still to replace or specify before the new turn resolver is complete:

- N−1 initial roll and Keep / Add / Reroll / Add+Reroll operation semantics;
- TN-derived fatigue and fatigue retention on bust;
- EF1–EF4, Threshold3–5 and VMA3–5 session matrix;
- per-session primary/secondary adaptations, RPE, bust tolerance and fatigue;
- independent physiological XP thresholds and milestone effects;
- fatigue-derived overtraining states;
- SL/SPEC preparation and the Training-to-Race conversion.

Do not interpret the existing direct-allocation resolver, fixed session fixtures,
CTL bridge, or old progression thresholds as approved rules for Training B.


## Decisions added — 2026-11-11

- Dice-derived fatigue retains the historical quasi-Fibonacci curve. The deviation
  from the full-pool TN is rounded upward with `ceil(final_energy - TN)`
  before the curve is evaluated. The resulting fatigue contribution is an
  integer and can represent either load or recovery.
- `training_v2.dice_progression` exposes explicit permanent operations:
  `add_die(state)` adds a d6 up to six dice, and
  `upgrade_die(state, index)` advances the player-selected die by one size.
  These operations define no milestone thresholds or automatic die selection.
- The existing direct-allocation `engine.py` still contains historical
  experimental progression hooks. It is not the target Training B turn
  resolver; the new progression operations are intentionally not wired to
  those obsolete thresholds.


## Main turn loop — 2026-11-11

The new `training_v2.turn.resolve_training_turn` connects the approved player
decisions in one deterministic turn pipeline:

1. Roll exactly N−1 dice; the reserve die is not rolled yet.
2. Choose Keep, Add, Reroll or Add+Reroll. Add rolls the reserve only after
   that choice; Add+Reroll resolves the reroll before rolling the reserve.
3. Allocate all final energy between EF, Seuil and VMA through the conserved
   `TrainingEnergyBudget`.
4. Apply the quasi-Fibonacci dice-fatigue contribution immediately and persist
   the turn count. A subsequent session bust must not undo this contribution.

The previous `engine.py` direct-dice-to-session path remains a historical
prototype and is not called by this new loop. Session-dose resolution is the
next integration step; the EF1–EF4 / Seuil3–5 / VMA3–5 matrix and its adaptation,
RPE/bust and session-fatigue values remain OPEN. No placeholder balance values
are silently promoted into the new loop.


## Session-dose resolution — 2026-11-11

The Training B turn can now resolve the complete dose layer through
`resolve_training_turn(..., choose_sessions=..., rpe_authorized=...)`.
The session callback receives the conserved EF / Seuil / VMA budget and returns
an ordered list of dose keys. The resolver validates that the exact session
doses consume each corresponding budget; no energy is converted into a
surplus or silently discarded.

### Base matrix — EXPERIMENTAL

The ten base entries are `EF1–EF4`, `SEUIL3–SEUIL5` and `VMA3–VMA5`.
The number in each key is the exact energy dose, not a physiological capacity,
adaptation amount or RPE. Each entry has independent primary XP, secondary XP,
RPE and session fatigue values in `training_v2/session_resolution.py`.
All these numerical values are **EXPERIMENTAL** and intended for simulation
and playtest calibration, not promoted design rules.

| Session | Dose | RPE | Primary XP | Secondary XP | Session fatigue |
|---|---:|---:|---:|---:|---:|
| EF1 | 1 | 1 | EF +1 | — | 0 |
| EF2 | 2 | 2 | EF +2 | Seuil +1 | 1 |
| EF3 | 3 | 3 | EF +3 | Seuil +1 | 2 |
| EF4 | 4 | 4 | EF +4 | Seuil +2 | 3 |
| SEUIL3 | 3 | 3 | Seuil +2 | EF +1 | 2 |
| SEUIL4 | 4 | 4 | Seuil +3 | EF +1 | 3 |
| SEUIL5 | 5 | 5 | Seuil +4 | EF +2 | 4 |
| VMA3 | 3 | 4 | VMA +2 | Seuil +1 | 3 |
| VMA4 | 4 | 5 | VMA +3 | Seuil +1 | 4 |
| VMA5 | 5 | 6 | VMA +4 | Seuil +2 | 5 |

EF1–EF3 may repeat up to their per-turn caps; EF4, Seuil and VMA entries
are limited to one occurrence each. These limits are also provisional.

### Bust — EXPERIMENTAL

For each session in plan order, calculate
`excess = max(0, session_RPE - rpe_authorized)`. If excess is positive,
roll the largest persistent die and bust when its **raw face** is less than
or equal to excess. The first bust cancels that session and every later
planned session. Successful earlier sessions retain their effects.

A successful session adds its primary and secondary XP to separate EF,
Seuil and VMA progression reserves and adds its session-specific fatigue.
A busted session adds neither adaptations nor session fatigue. Dice-derived
fatigue is already committed before this resolution and is never rolled back.
Physiological profile thresholds and automatic profile changes remain OPEN;
this layer records XP but does not invent milestone thresholds.

The bust comparison, the complete matrix, fatigue values and repetition caps
are intentionally marked EXPERIMENTAL. The caller supplies `rpe_authorized`;
its derivation from the dice/turn context remains an integration parameter
to calibrate, not a hidden rule.
