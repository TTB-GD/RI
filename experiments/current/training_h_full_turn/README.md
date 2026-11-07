# Training H — full-turn and multi-turn prototype

**Status: EXPERIMENTAL / isolated prototype.** This increment does not modify
the production Training engine or promote any rule to GDD CURRENT.

## Turn sequence

1. Roll the initial active dice: n-1 dice; the smallest permanent die remains
   in reserve (ties leave the last die in reserve).
2. The player explicitly chooses Keep, Reroll, Add, or Add+Reroll.
3. TN is calculated from the full permanent pool, including the reserve.
4. Energy is the sum of the final retained dice. Blackjack fatigue is computed
   once from that energy versus TN, before session risk is resolved.
5. The player supplies an EF/Quality budget split and an ordered session plan.
6. A supplied bust index resolves the plan. The failed session grants no
   progression or session-specific fatigue. Successful sessions remain
   completed; later risky sessions are cancelled under the inherited legacy
   convention. No post-bust EF redistribution is performed.
7. Imbalance fatigue and intrinsic session fatigue use completed sessions
   only. Blackjack fatigue is never rolled back by a bust.

## Multi-turn state

At turn start, overtraining is active when `fatigue > fatigue_limit(pool_size)`.
The permanent dice pool is unchanged. While overtraining is active, Add and
Add+Reroll are rejected; Keep and Reroll remain available. The condition is
evaluated at turn start: recovery during a turn restores reserve access on the
following turn, not retroactively during the current turn.

At turn end:

`fatigue_end = max(fatigue_floor, fatigue_start + blackjack + imbalance + intrinsic)`

- Blackjack fatigue is based on final dice results versus TN.
- Imbalance and intrinsic fatigue are based on completed sessions.
- A negative blackjack result can reduce accumulated fatigue.
- No additional recovery is awarded for an EF-heavy split.
- Fatigue limits and the floor are injected fixtures, not approved balance.

## Progression and catalogue

- Completed sessions add fixed adaptation points to named progression tracks.
- Milestones convert accumulated track points into profile gains exactly once.
- Local milestones can unlock local catalogue options; a separate GLOBAL track
  can unlock SL/SPEC options.
- Eligibility and acquisition are distinct. A milestone makes options
  available to acquire; it does not automatically add them to the portfolio.
- Acquisition is an explicit player choice and can happen in the same turn as
  the milestone.
- Session adaptations, GLOBAL progression, milestone thresholds, profile
  gains and unlocks are injected fixtures. This prototype does not decide how
  the game's global development track is calculated.

## Scope and limitations

- No automatic player policy, no D99, no cooperation, no pool-size upgrades.
- No multi-player synchronization or Race conversion.
- No production integration and no GDD CURRENT changes.
- This is a deterministic state-transition harness, not a strategy simulation.
  It validates state composition over 3, 6, 12 and 16 turns; it does not
  establish that the resulting game is balanced or strategically rich.

## Run

```bash
pytest -q experiments/current/training_h_full_turn
```
