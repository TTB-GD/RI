# Bust Trigger Harness

Status: **CURRENT EXPERIMENT — NOT PRODUCTION BEHAVIOR**

## Question

Characterize the missing upstream risk/bust trigger before `session_resolution.resolve_session_plan()` without changing production rules.

The current production selector rejects sessions whose RPE exceeds the turn's `rpe_max`. Therefore production cannot currently generate the risky quality sessions that the post-bust resolver knows how to resolve.

## Candidate rule characterized

This harness isolates the historical Fatigue V1 candidate rule:

- a quality session is risky when `session_rpe > rpe_max`;
- overshoot = `session_rpe - rpe_max`;
- use the largest die size in the player's current pool as the risk die;
- the session busts when `risk_roll <= overshoot`;
- risky sessions are tested in planned order;
- the first bust stops later risk tests;
- post-bust consequences remain the responsibility of `session_resolution.resolve_session_plan()`.

The "largest die in the current pool" choice is an **EXPERIMENTAL POLICY ASSUMPTION** in this harness. It is not promoted to production by this experiment.

## Representation audit and ambiguity

Production exposes the persistent pool as `PlayerDicePool.sizes`, a list of
supported sizes, and can materialize it as `Die` objects. It does **not** expose
a named "best die" or "risk die". Turn rolling separately partitions that pool
into active dice plus the smallest reserve die. Consequently, "best die" could
mean the largest size in the complete persistent pool (the harness assumption),
the largest active die for that turn, or a separately designated risk die. The
repository does not currently settle that choice.

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
- the current selector's inability to plan a risky quality session.

No production files, GDD rules, selector weights, Fatigue V1 parameters or post-bust rules are modified.

## Run

```bash
python experiments/current/bust_trigger/run.py
python -m unittest experiments.current.bust_trigger.test_harness -v
```
