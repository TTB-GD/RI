# Bust Trigger Harness

Status: **CURRENT EXPERIMENT — BASE RULE NOW IN PRODUCTION**

## Question

Retain the deterministic characterization and probability analysis of the
upstream risk/bust trigger now used before `session_resolution.resolve_session_plan()`.

Production now admits catalogue-eligible risky qualities and delegates the
first generated `bust_index` to the existing post-bust resolver.

## Candidate rule characterized

This harness isolates the historical Fatigue V1 candidate rule:

- a quality session is risky when `session_rpe > rpe_max`;
- overshoot = `session_rpe - rpe_max`;
- use the largest die size in the player's current pool as the risk die;
- the session busts when `risk_roll <= overshoot`;
- risky sessions are tested in planned order;
- the first bust stops later risk tests;
- post-bust consequences remain the responsibility of `session_resolution.resolve_session_plan()`.

The "largest die in the current pool" choice is now the CURRENT production
rule. The harness remains useful for deterministic scenarios and its exact
probability matrix; it is not an independent production engine.

## Representation audit

Production exposes the complete persistent pool as `PlayerDicePool.sizes` and
materializes supported sizes as `Die` objects. The CURRENT rule explicitly
selects `max(PlayerDicePool.sizes)`, independently of the active/reserve split
used for the turn budget.

The harness uses a uniform raw face in `1..max(pool_sizes)`. This currently
equals `Die.roll()`'s final value because every configured die bonus is zero;
the distinction would matter if bonuses were enabled later.

## Exact candidate probabilities

For die size `S` and positive overshoot `k`, the candidate probability is
`min(k, S) / S`; at zero or negative overshoot there is no test and probability
zero.

| Overshoot | d6 | d8 | d10 | d12 |
|---:|---:|---:|---:|---:|
| 1 | 1/6 | 1/8 | 1/10 | 1/12 |
| 2 | 2/6 | 2/8 | 2/10 | 2/12 |
| 3 | 3/6 | 3/8 | 3/10 | 3/12 |
| 4 | 4/6 | 4/8 | 4/10 | 4/12 |

## What the harness measures

- deterministic boundary cases for risk/no-risk and bust/pass;
- exact theoretical bust probability by overshoot and die size;
- ordered multi-risk examples and first-bust stopping;
- the production selector's ability to plan an eligible risky quality session.

The harness shares the production base-threshold function. It does not alter
selector weights, Fatigue V1 parameters or post-bust rules.

## Run

```bash
python experiments/current/bust_trigger/run.py
python -m unittest experiments.current.bust_trigger.test_harness -v
```
