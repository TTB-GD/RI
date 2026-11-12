# Race V2 — prototype multi-secteur

**PROTOTYPE / EXPERIMENTAL — NOT A COMPLETE GAME LOOP.**

This isolated prototype implements the current multi-sector Race V2 flow described
by `docs/game-design/RACE_V2_DESIGN.md`. The validated design and the executable
prototype must remain distinct: code presence does not validate balance or
Training integration.

## Included

- 5 km / 10 km / half-marathon / marathon: 7 / 10 / 13 / 16 sectors;
- explicit integer energy-to-speed physiology table;
- sector resolution with VMA expenditure/conversion caps, terrain and aspiration;
- sustainability balance from initial credit, revealed form and actual consumption;
- 3d6 form-of-day roll, category recipe and shuffled card decks;
- scheduled card reveals at sector start;
- cumulative integer score and adjacent-gap group / hare / aspiration calculation;
- complete dice-pool rolls, individual rerolls and free subset selection;
- global non-regenerating reroll capital;
- two-phase sector flow: reveal and roll, then validate decisions and resolve.

## Sector decision sequence

1. Reveal any scheduled form card before the dice roll.
2. Update the cumulative form balance and display the current group status/bonus.
3. Roll every die in each player's pool.
4. Apply individual rerolls, each consuming one unit of global capital.
5. Select any subset of dice to spend, including the empty subset.
6. Resolve all players' expenditures and update score, sustainability and next-sector groups.

A selected empty subset produces no speed and no sustainability consumption.
Unselected dice are not carried forward; the full pool is rolled next sector.
A die may be rerolled more than once if global capital remains. No reroll occurs
after subset selection.

## Player configuration boundary

`RacePlayerConfig` currently receives explicit inputs:

- integer physiology table and its EF / Seuil / VMA energy anchors;
- course-specific `specific_pace`;
- initial sustainability credit `initial_credit` (the design quantity `S0`);
- `dice_sizes` from the persistent Training pool;
- `affutage_level` in 0..4.

The reroll budget is:

`ceil(Rmax_5km × (N / 7) × P_affûtage)`

where `P_affûtage` maps tiers 0..4 to 0, 0.25, 0.50, 0.75 and 1.
The thresholds for deriving the tier from residual Training fatigue are in the
Race V2 design specification. The prototype accepts the tier as an input; it
does not derive it from Training.

## Explicit non-goals / gaps

- No automatic Training B → Race player configuration.
- No derivation of the physiology table from a Training B state.
- No derivation of course-specific AS.
- No calculation of initial credit `S0` from Training.
- No residual-fatigue → affûtage-tier adapter.
- No human-play balance validation or final calibration.

The earlier `RACE_RESERVE_DESIGN.md` preparation-reserve equation is superseded
as Race design by the validated `S0 + F - C` balance. It remains in the
repository for historical traceability.

## Determinism and validation

RNG streams are seeded independently per player. A sector is prepared before
choices are submitted. Invalid decisions are validated atomically: they do not
consume reroll capital or resolution RNG state, and the pending dice/cards
remain available for a valid decision.

## Tests

```bash
python -m unittest experiments.current.race_v2_prototype.test_sector -v
python -m unittest experiments.current.race_v2_prototype.test_race -v
python -m unittest experiments.current.race_v2_prototype.test_dice -v
python -m unittest experiments.current.race_v2_prototype.test_dice_session -v
```

These commands describe the available test suites; they are not a claim that a
new test run was executed during this documentation-only change.
