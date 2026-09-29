# Training V2 → Race V2 minimal bridge


> **EXPERIMENTAL SPEC PROBE — SPEC IS OPEN / NOT IMPLEMENTED.** This is not
> the integrated V2 baseline. SPEC is
> OPEN and not implemented in the active Race V2 path; Position, Efficacité and
> AS42/AS21/AS10/AS5 below are preserved experimental conventions only.

**EXPERIMENTAL ONLY — NOT CURRENT GAME DESIGN**

This isolated probe connects synthetic Training V2 SPEC allocations to the
existing experimental Race Engine V2 primitives. It changes neither production
code nor CURRENT tests, and it does not simulate training longitudinally.

## Scope and fixed fixtures

- Two contexts only: AS42 starts at 17 (`15 EF < 17 < 21 Seuil`) and AS10 at
  22 (`21 Seuil < 22 < 27 VMA`). These are probe parameters, not design values.
- One shared physiology (EF 15, Seuil 21, VMA 27), `6d6` pool, Curve B, six
  flat segments, CTL 100, freshness 0, and FORM_PATTERN.
- 20 shared seeds × 2 contexts × 3 builds = 120 courses.
- Four SPEC tiers per build: SPEED 4/0, BALANCED 2/2, ECONOMY 0/4
  (POSITION/EFFICIENCY). Impossible tiers are reported, never converted.
- `ECO_MAX = min(C0(AS)-C0(EF), C0(VMA)-C0(AS))`; effective ECO is capped by
  that envelope and applies at the exact active AS only. The cost floor is C0(EF).

## Reuse and experimental adapter

The harness imports the unchanged Race Engine V2 dice generation, persistent
pool fixture, subset enumeration, form classification, reserve mapping and
Curve B cost function. Since its normative runner has no cost-adapter hook, the
local runner preserves its segment order and reserve-finalization rule while
injecting effective cost only at exact AS.

`SPEC_TARGET_SUSTAINABLE` is the sole experimental policy. It selects the
highest rolled subset Production at or below active AS that leaves one EF-cost
unit per future segment; if none is sustainable it selects the cheapest payable
option. It contains no build label or bonus. Ties are deterministic. POSITION
changes only its AS target; it does not change pool, roll, reserve, freshness or
difficulty.

Run:

```bash
python -m experiments.current.training_race_bridge.harness
python -m unittest experiments.current.training_race_bridge.test_harness -v
```

`results.json` contains protocol, synthetic athletes, aggregate metrics, all
required seed-paired differences, and per-course traces.
