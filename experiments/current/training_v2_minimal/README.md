# Training V2 minimal

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

This isolated harness probes the proposed EF/Quality dice partition, true
multi-quality composition, Q-spent/SPEC accounting, 16-turn progression, and
Speed/Economy SPEC profiles. It imports only the existing D99
This isolated harness probes the proposed EF/Quality dice partition, 16-turn
progression, and Speed/Economy SPEC profiles. It imports only the existing D99
pattern signature and Race Engine V2 Curve B cost boundary; it does not call or
change the production decision engine, Fatigue V1, or a complete race.

Run from the repository root:

```bash
python -m experiments.current.training_v2_minimal.harness
python -m unittest experiments.current.training_v2_minimal.test_harness -v
```

The module command updates only A2/B2 in the existing result file; it does not
rerun the larger first-pass B campaign. `run_all()` remains available only for
an explicit full regeneration.

Modelling conventions and measured results are recorded in `REPORT.md`;
machine-readable aggregate results are in `results.json`; the three first-pass
representative trajectories per policy remain preserved there.
Modelling conventions and measured results are recorded in `REPORT.md`;
machine-readable aggregate results and three representative trajectories per
policy are in `results.json`.
