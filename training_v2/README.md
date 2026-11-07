# Training B — first playable turn and catalogue foundation

**EXPERIMENTAL — target architecture selected on 2026-11-07.** Training CURRENT is a historical reference scheduled for retirement; this package is the active implementation path.

This package is the first executable vertical slice of Training B. It remains
isolated from the historical CURRENT implementation; no compatibility layer
or hybrid dependency is introduced.

## Playable loop

The turn is deliberately split into three phases:
1. roll the persistent pool with `roll_pool` and inspect the retained values;
2. call `list_program_options(state, roll)` to enumerate every feasible
   physical dice partition and affordable quality programme;
3. choose one returned option and pass its indices and qualities to
   `resolve_turn`.

The option enumerator is deliberately neutral: it does not rank, score, or
select a preferred programme. It includes the empty quality programme, so
unspent Q energy can progress the experimental SPEC counter.

## Interactive console

Run a persistent one-player session from the repository root:

~~~bash
python -m training_v2
~~~

Each turn displays the retained roll and all feasible programmes. Enter the
number of a programme to resolve it; press Enter to continue with the same
player state, or enter `q` to stop. The console is a thin interface over the
engine and introduces no automatic programme selection.

Example:

~~~python
from training_v2 import PlayerState, roll_pool, list_program_options, resolve_turn

player = PlayerState()
roll = roll_pool(player)
options = list_program_options(player, roll)
choice = options[0]  # Replace with an explicit player choice.
result = resolve_turn(
    player, roll.raw_faces,
    choice.ef_indices, choice.quality_indices, choice.qualities,
)
print(result)
print(player.profile, player.dice_pool, player.fatigue)
~~~

## Experimental boundaries made explicit

- Initial profile: EF 6 / Seuil 8 / VMA 10.
- Quality cost and progression thresholds reproduce the B2 experimental
  harness, not a final calibration.
- EF milestones: 10, 20, 35, 50, 70, 100, 120, 150. At 35 and 100, a d6 is
  added instead of raising EF; other milestones raise EF by one only while
  EF remains below Seuil.
- Quality milestones: 7, 15, 25, 35, 50, 65, 80, 100. The milestones 15,
  35, 65 and 100 grant one pool upgrade, with a four-upgrade ceiling.
- Successful Seuil/VMA sessions raise their respective local marker by one.
- Unassigned Quality energy advances the SPEC progression counter. Quality
  energy assigned to a session that busts is lost. This is the B2
  Q_SPENT_SPEC accounting variant.
- Fatigue uses the existing experimental blackjack curve plus the D1-F3
  excess-quality term. Session-specific fatigue is zero in this first pass;
  it remains an explicit catalogue field for later calibration.
- The initial quality catalogue contains Seuil and VMA. Each entry now declares
  its family, load type, fixed profile adaptations, specific fatigue and
  per-turn limit. The engine applies the declared adaptations generically,
  including multidimensional entries.
- The B2 cost formula remains experimental. RPE as a separate session field,
  selectable EF sessions, SL/SPEC acquisition, permanent portfolio rules,
  and Race conversion are not implemented yet.

## Known limitations

- The console is a one-player terminal playtest interface, not a graphical UI
  or complete multiplayer game.
- Risk uses the largest die size as the risk-roll range, matching the B2
  harness convention. This remains experimental.
- EF and Quality must both receive at least one retained die and EF energy
  must be at least Quality energy, matching the A/B2 partition experiment.

Run tests:

~~~bash
python -m unittest discover -s tests -p 'test_training_v2.py' -v
~~~
