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
