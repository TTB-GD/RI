# Training H — full-turn prototype

**Status: EXPERIMENTAL / isolated prototype.** This increment does not modify
the production Training engine or promote any rule to GDD CURRENT.

## Turn sequence represented

1. Roll the initial active dice: n-1 dice; the smallest permanent die remains
   in reserve (ties leave the last die in reserve).
2. The player explicitly chooses Keep, Reroll, Add, or Add+Reroll.
   The harness receives that choice; it never selects an action automatically.
3. TN is calculated from the full permanent pool, including the reserve.
4. Energy is the sum of the final retained dice. Blackjack fatigue is computed
   once from that energy versus TN, before session risk is resolved.
5. The player supplies an EF/Quality budget split and an ordered session plan.
6. A supplied bust index resolves the plan. The failed session grants no
   progression token or session-specific fatigue. Later risky sessions are
   cancelled; later safe sessions remain eligible, following the legacy
   resolution convention. No post-bust EF redistribution is performed.
7. Imbalance fatigue and intrinsic session fatigue use completed sessions
   only. Blackjack fatigue is never rolled back by a bust.

## Scope and explicit limits

- Deterministic inputs for dice actions and risk outcomes; no automated policy.
- Overtraining can disable Add and Add+Reroll; no fatigue threshold/regulation
  is implemented in this increment.
- Session catalogue costs, intrinsic penalties, and progression tokens are
  fixtures supplied by the caller, not approved balance values.
- D99 pattern effects, cooperative rules, profile milestone conversion,
  multi-turn persistence, and recovery regulation are not implemented.
- The current legacy post-bust redistribution rule is deliberately omitted.
  Whether H should permit player-chosen redistribution remains OPEN.
- The convention that later risky sessions are cancelled after a bust is
  inherited from the existing resolver and should be reviewed against H.

## Run

```bash
pytest -q experiments/current/training_h_full_turn
```
