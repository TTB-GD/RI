# Training V2 minimal

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN.**

This isolated harness probes the proposed EF/Quality dice partition, 16-turn
progression, and Speed/Economy SPEC profiles. It imports only the existing D99
pattern signature and Race Engine V2 Curve B cost boundary; it does not call or
change the production decision engine, Fatigue V1, or a complete race.

Run from the repository root:

```bash
python -m experiments.current.training_v2_minimal.harness
python -m unittest experiments.current.training_v2_minimal.test_harness -v
```

Modelling conventions and measured results are recorded in `REPORT.md`;
machine-readable aggregate results and three representative trajectories per
policy are in `results.json`.
