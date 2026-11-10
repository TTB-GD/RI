# Training B — 16-turn trajectory probe

**EXPERIMENTAL diagnostic harness. Not a balance calibration.**

Runs three transparent allocation heuristics (balanced, EF-focused, Quality-focused) over 16 turns with three fixed random seeds each. It records successful sessions, busts, realized EF/Quality energy, local progression, physiology, fatigue, dice-pool changes, eligibility and explicit portfolio acquisitions.

The unlock thresholds (EF 28, Seuil 8, VMA 8) and the policy weights are deliberately illustrative fixtures. They are not proposed game rules. The acquisition policy in this probe chooses every newly eligible option immediately; this isolates the availability and effect of the catalogue rather than testing acquisition-choice strategy.

Run from repository root:

~~~bash
python -m experiments.current.training_b_trajectory.harness
~~~

## Interpretation limits

- This tests reproducibility and whether the current rules produce distinguishable 16-turn profiles.
- It does not test multiplayer interaction or Training-to-Race transfer.
- The engine currently accumulates fatigue but does not make fatigue constrain the next turn's dice pool. Fatigue totals are therefore diagnostic only; load regulation is not validated.
- Current session adaptations are fixed per successful session, not scaled by invested energy.
- The policy score is a transparent heuristic used to create contrasting play traces, not a model of optimal player behavior.
- The random seeds are scenario coverage, not statistical balance evidence.
