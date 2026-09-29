# Race V2 — micro-sonde Charge au-dessus de VMA

**EXPERIMENTAL COUNTERFACTUALS — NOT CURRENT BEHAVIOR.**

Cette sonde analytique compare trois traitements minimaux lorsque
`Production <= VMA` mais `Production + Difficulty > VMA`. Elle ne modifie ni
le domaine intégré de `physiological_cost`, ni Race V2, ni le GDD. Les variantes
B et C sont calculées localement et ne constituent pas des propositions validées.

La grille exhaustive contient 3 profils × 4 Productions × 4 Difficulties, soit
48 configurations déterministes. Aucun RNG, tour ou course n'est utilisé.

```bash
python -m experiments.current.above_vma_probe.probe
python -m unittest experiments.current.above_vma_probe.test_probe -v
```

`results.json` est l'artefact machine reproductible. `REPORT.md` synthétise les
faits, résultats, observations, interprétations, limites et questions de design.
