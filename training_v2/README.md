# Training V2 — first playable turn

**EXPERIMENTAL ONLY — does not change CURRENT game rules.**

This package is the first executable vertical slice of Training V2. It keeps
the existing player simulation, CURRENT catalogue, selector, risk resolver,
and dice progression untouched.

## Playable loop

A caller supplies:
1. the raw dice faces (or asks the roll helper to roll the persistent pool);
2. a physical partition of retained dice into EF and Quality compartments;
3. the quality sessions selected by the player.

The engine validates the allocation, checks that the selected quality
programme is affordable, resolves risky quality sessions, applies successful
local adaptations, updates EF / Quality / SPEC progression, applies the
provisional pool milestones, and carries fatigue and player state into the
next turn.

Example:

~~~python
from training_v2 import PlayerState, roll_pool, resolve_turn

player = PlayerState()
result = resolve_turn(
    player,
    raw_faces=(6, 6, 6, 6),
    ef_indices=(0, 1),
    quality_indices=(2, 3),
    planned_qualities=("SEUIL",),
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
- The initial catalogue contains Seuil and VMA. SL/SPEC session acquisition,
  permanent portfolio rules, player-facing programme selection, and Race
  conversion are deliberately not implemented in this slice.

## Known limitations

- Dice partition and programme selection are supplied by the caller; no AI
  policy or UI is included.
- Risk uses the largest die size as the risk-roll range, matching the B2
  harness convention. This remains experimental.
- EF and Quality must both receive at least one retained die and EF energy
  must be at least Quality energy, matching the A/B2 partition experiment.
- This first slice is a rules engine API, not yet a complete turn interface.

Run tests:

~~~bash
python -m unittest discover -s tests -p 'test_training_v2.py' -v
~~~
