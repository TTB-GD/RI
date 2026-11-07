# Training allocation architecture — D / P / H

**Status: EXPERIMENTAL.** This probe supports the selected direction **H**
(compartments EF/Qualité, then session catalogue). It does not amend the GDD or
the production engine.

## Models

- **D — direct:** every retained die is assigned to one session occurrence.
- **P — compartments:** retained dice are split into EF and Quality budgets;
  there is no session catalogue in this variant.
- **H — hybrid:** dice are split into EF and Quality budgets, then sessions
  are bought from their matching compartment. EF may repeat; Seuil and VMA
  are each limited to one occurrence in this first catalogue.

## Controlled scope

- Exhaustive 4d6 raw outcomes: 1,296.
- Same roll resolution for all models: D99_OFF, retain the highest three dice.
- Current experimental catalogue costs: EF 2, Seuil 4, VMA 5.
- TN is the expected total of the persistent pool: 14 for 4d6.
- Blackjack fatigue is independent of D/P/H allocation.
- EF/Quality imbalance is measured as ceil(max(0, Q - EF) / 2), both on
  allocated budgets and on energy actually spent on sessions.

## Modelling choices and limits

1. EF > Quality is **not** a hard legality constraint. The split is retained
   and its imbalance penalty is measured. This distinguishes a preference
   from a prohibition.
2. Session affordability is compartment-specific in H: EF sessions spend EF
   budget; Seuil/VMA spend Quality budget. Unspent energy remains unspent.
3. A completed session yields a progression token on its corresponding track.
   The harness does not convert tokens directly into profile gains: milestones
   and carry-over remain OPEN.
4. Risk/bust is not simulated. Sessions are assumed completed when affordable.
   A later increment must resolve risk and fatigue from completed sessions only.
5. Session costs and VMA-specific fatigue are provisional catalogue fixtures.

## Run

```bash
python -m experiments.current.training_allocation_harness.harness
pytest -q experiments/current/training_allocation_harness
```

The output is deterministic JSON. The harness is isolated from production code.
