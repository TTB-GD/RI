# Training B — direct dice-to-session allocation

**EXPERIMENTAL — target architecture selected on 2026-11-07.** Training CURRENT is historical and is not a compatibility target.

## Playable loop

1. Roll the persistent dice pool.
2. Enumerate feasible compositions from the session catalogue.
3. Assign every retained die to exactly one session occurrence.
4. Choose a composition; the engine resolves risk, adaptations, progression and fatigue.

There is no separate EF-dice / Quality-dice partition. Each session declares its family, load type, fixed adaptations, energy cost, RPE, specific fatigue and optional per-turn occurrence limit. The player can repeat EF sessions; Seuil and VMA are limited to one occurrence each in this initial fixture. The option enumerator does not rank or select a composition.

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
- The unused energy assigned to Quality sessions continues to feed the experimental SPEC counter. SPEC itself remains OPEN and this accounting is temporary.
- A bust stops subsequent session resolution; the busted session receives no adaptation or progression.
- Fatigue still uses the existing experimental blackjack term, the excess Quality-over-EF term, and specific session fatigue. Calibration is deferred.

## Known limitations

- This is a one-player terminal prototype, not multiplayer or a graphical UI.
- Initial profile is EF 6 / Seuil 8 / VMA 10.
- Volume milestones remain experimental B2 fixtures and add dice at selected thresholds; physiological EF gains come from successful EF sessions, not from a second automatic EF increase. Fatigue remains experimental.
- SL, SPEC acquisition, permanent session portfolio, combinations, and Training-to-Race conversion are not implemented.
- Risk uses the largest persistent die as the risk-roll range; this remains experimental.

Run tests:

~~~bash
python -m unittest discover -s tests -p 'test_training_v2*.py' -v
~~~
