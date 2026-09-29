# Course V2 — sonde Position / Efficacité

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

Cette expérience analytique isolée compare deux courbes natives dans le domaine
`EF=0 ... VMA=10`, puis applique exactement l'enveloppe proposée :

`ECO_MAX(AS) = min(C0(AS)-C0(EF), C0(VMA)-C0(AS))`.

Elle n'importe ni ne modifie Fatigue V1, Race Engine V2, Training V2, les
expériences SPEC antérieures, le GDD ou les tests CURRENT. Une unité
d'Efficacité retire une unité de coût, sous réserve de l'enveloppe. Dans E4,
l'Efficacité est spécifique à l'AS active : les deux allures adjacentes sont
des contre-factuels locaux au coût natif. Cette convention expérimentale évite
d'inventer une zone d'effet.

Exécution reproductible, sans RNG ni Monte-Carlo :

```bash
python -m experiments.current.race_efficiency_probe.harness
python -m unittest experiments.current.race_efficiency_probe.test_harness -v
```

`results.json` contient les tables exhaustives E1–E4 et les rendements
marginalaux. `REPORT.md` en donne la synthèse utile à la décision.
