# Run It — Current State

Last consolidated: 2026-09-24  
Canonical branch: `main`  
Implementation baseline: `231d49e729431c48ce24ebcdd55871b9f9f76302`

This file is the fast-entry snapshot for the current prototype state. It does not replace the GDD. When this file, the GDD and the code disagree, follow the authority hierarchy in `AGENTS.md` and report the divergence explicitly.

## CURRENT IMPLEMENTATION

- `Player` keeps a persistent `PlayerDicePool` across turns.
- Initial pool: 4d6.
- +1 d6 at cumulative CTL 50 and 100, available from the following turn.
- Die upgrades use the current d6 → d8 → d10 → d12 progression, with a global maximum of 4 upgrades.
- D99 defines the maximum number of quality sessions that may be planned for the turn.
- SL counts against the D99 quality cap.
- EF sessions are repeatable within the turn.
- Each quality catalogue entry may appear at most once per turn.
- SL remains limited to at most one session per turn.
- Quality sessions must not outnumber EF sessions in the same turn.
- Maximum 7 counted sessions per turn.
- Post-bust session resolution is implemented:
  - the session that busts counts toward the 7-session limit;
  - its energy is lost;
  - it produces no CTL/progression;
  - later risky quality sessions are cancelled;
  - their planned energy may be redistributed into EF work, subject to remaining session slots and RPE accessibility.
- A risky quality session is currently identified relative to the turn's RPE Max: `session RPE > rpe_max`.
- CTL, progression and turn fatigue use effective realised load after post-bust resolution.
- Targeted production tests cover D99, repetition, SL, the 7-session cap and post-bust resolution.
- A deterministic current harness exists at `experiments/d99_bust_resolution/run.py`.

## CURRENT LIMITATIONS / OPEN IMPLEMENTATION

- The upstream production trigger/roll that determines whether a risky quality session actually busts is not yet implemented in the production turn flow.
- `resolve_session_plan()` can resolve a bust when `bust_index` is supplied; this is a resolution layer, not yet the complete risk engine.
- Fatigue V1 remains experimental and is not yet the definitive production fatigue model.
- The current session selector remains a technical weighted/greedy baseline, not a final human-player model.
- The Standard Training Player remains experimental.
- The race system is not implemented.
- The future race role of SL is designed conceptually but not yet implemented as race access/success logic.

## CURRENT DESIGN DECISIONS THAT AFFECT IMPLEMENTATION

- D99 is a hard cap on quality opportunities for the turn, including SL.
- A quality slot consumed by a busted or cancelled quality session is not refunded.
- EF is repeatable.
- Quality catalogue entries are unique per turn.
- SL is unique per turn and also limited to 1 maximum.
- After the first bust:
  - the busted session loses its energy;
  - later risky quality sessions are no longer tested as quality;
  - their quality slots remain lost;
  - their energy may be reassigned to EF work within the 7-session cap.
- SL is intended as a race-specific preparation dimension rather than an intrinsically superior generic training choice.

## HISTORICAL / NOT CURRENT BEHAVIOR

The following experimental families are historical evidence only and must not be used as the current prototype reference unless explicitly re-run against the current rules:

- Fatigue V1 large campaigns;
- Overtraining Capacity experiments;
- P0 selector audit;
- Standard Player / bundle-risk experiments run before the consolidated D99, repetition, SL and post-bust corrections.

Their principal conclusions remain useful for design traceability, but their numeric outputs are not current baseline metrics.

## CURRENT REPOSITORY CONVENTION

- `tests/` = tests of current prototype behavior.
- `experiments/current/` = optional location for experiments that still describe the current rules.
- `experiments/archive/` = historical experiments retained only for traceability.
- Historical experiment tests belong with their experiment, not in production `tests/`.
- Historical experiments should be marked: `HISTORICAL — NOT CURRENT BEHAVIOR`.

The existing `experiments/d99_bust_resolution/` harness is current and predates this directory convention; it may remain where it is until a future cleanup requires moving it.

## NEXT DEVELOPMENT TARGETS

Priority technical questions currently open:

1. characterize and then implement/specify the production risk/bust trigger before `resolve_session_plan()`; a current deterministic harness now exists at `experiments/current/bust_trigger/`, while production remains unchanged;
2. continue Fatigue V1 design work without silently replacing the current model;
3. re-evaluate the Standard Training Player only against the corrected D99/repetition/SL/bust rules;
4. implement race objectives and the concrete role of SL when their design thresholds are validated.

## TASK CLOSURE SNAPSHOT

For any significant production change, the final report should include:

```text
CURRENT:
- what changed in current behavior

OPEN:
- unresolved limitations or design questions

GITHUB:
- main up to date: yes/no
- reference commit / PR: ...
```

If the task created a local commit that is not on GitHub, the Git status rules in `AGENTS.md` take precedence.
